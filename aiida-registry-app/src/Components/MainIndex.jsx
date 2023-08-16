import { useState } from 'react';
import { Link, Route, Routes } from 'react-router-dom';
import jsonData from '../plugins_metadata.json'
import base64Icon from '../base64Icon';
import Box from '@mui/material/Box';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';

const globalsummary = jsonData["globalsummary"]
const plugins  = jsonData["plugins"]
const status_dict = jsonData["status_dict"]
const length = Object.keys(plugins).length;
const currentPath = import.meta.env.VITE_PR_PREVIEW_PATH || "/aiida-registry/";

function MainIndex() {
    const [sortOption, setSortOption] = useState('alpha');
    const [sortedData, setSortedData] = useState(plugins);
    document.documentElement.style.scrollBehavior = 'auto';

    function setupScrollBehavior() {
      var prevScrollpos = window.scrollY;
      window.onscroll = function() {
      var currentScrollPos = window.scrollY;
        if (prevScrollpos > currentScrollPos) {
          document.querySelector("header").style.top = "0"; //Display the header when scrolling up.
        } else {
          if (prevScrollpos > 150) {
          document.querySelector("header").style.top = "-155px"; //Hide the header when scrolling down.
          }
        }
        prevScrollpos = currentScrollPos;
      }
    }
    setupScrollBehavior();

    const handleSort = (option) => {
      setSortOption(option);


      let sortedPlugins = {};
      if (option === 'commits') {
        const pluginsArray = Object.entries(plugins);

        // Sort the array based on the commit_count value
        pluginsArray.sort(([, pluginA], [, pluginB]) => pluginB.commits_count - pluginA.commits_count);

        // Create a new object with the sorted entries
        sortedPlugins = Object.fromEntries(pluginsArray);
      }
      else if (option == 'alpha') {
        sortedPlugins = plugins;
      }
      else if (option == 'release') {
        //Sort plugins by the recent release date
        const pluginsArray = Object.entries(plugins);
        pluginsArray.sort(([, pluginA], [, pluginB]) => {
          if (!pluginA.metadata.release_date && !pluginB.metadata.release_date) {
           return 0; // Both plugins have no release date, keep them in the current order
          } else if (!pluginA.metadata.release_date) {
            return 1; // Only pluginB has a release date, so pluginA should come first
          } else if (!pluginB.metadata.release_date) {
            return -1; // Only pluginA has a release date, so pluginB should come first
          } else {
            return new Date(pluginB.metadata.release_date) - new Date(pluginA.metadata.release_date);
          }
        });

        // Convert the sorted array back to an object
        sortedPlugins = Object.fromEntries(pluginsArray);
      }

      setSortedData(sortedPlugins);
    };
    return (
      <main className='fade-enter'>

      <h2>Registered plugin packages: {length}</h2>
      <div className='globalsummary-box'>
        <div style={{display: 'table'}}>
        {globalsummary.map((summaryentry) => (
            <span className="badge" style={{ display: 'table-row', lineHeight: 2 }} key={summaryentry.name}>
            <span style={{ display: 'table-cell', float: 'none', textAlign: 'right' }}>
              <span className={`badge-left ${summaryentry.colorclass} tooltip`} style={{ float: 'none', display: 'inline', textAlign: 'right', border: 'none' }}>
                {summaryentry.name}
                {summaryentry.tooltip && <span className="tooltiptext">{summaryentry.tooltip}</span>}
              </span>
            </span>
            <span style={{ display: 'table-cell', float: 'none', textAlign: 'left' }}>
              <span className="badge-right" style={{ float: 'none', display: 'inline', textAlign: 'left', border: 'none' }}>
                {summaryentry.total_num} plugin{summaryentry.total_num !== 1 ? 's' : ''} in {summaryentry.num_entries} package{summaryentry.num_entries !== 1 ? 's' : ''}
              </span>
            </span>
          </span>
        ))}
        </div>
      </div>
      <div id='entrylist'>
        <h1 style={{display: 'inline'}}>
          Package list
      </h1>
          <Box sx={{ minWidth: 120 }} style={{display:'inline', padding:'20px'}}>
            <FormControl style={{width:'25%'}}>
              <InputLabel id="demo-simple-select-label">Sort</InputLabel>
              <Select
                value={sortOption} label = "Sort" onChange={(e) => handleSort(e.target.value)}
              >
                <MenuItem value= 'alpha'>Alphabetical</MenuItem>
                <MenuItem value='commits'>Commits Count</MenuItem>
                <MenuItem value='release'>Recent Release</MenuItem>
              </Select>
            </FormControl>
          </Box>

        {Object.entries(sortedData).map(([key, value]) => (
          <div className='submenu-entry' key={key}>
            <Link to={`/${key}`}><h2 style={{display:'inline'}}>{key} </h2></Link>
            {value.is_installable === "True" && (
              <div className='classbox' style={{backgroundColor:'transparent'}}>
               <CheckCircleIcon style={{color:'green', marginBottom:'-5'}}/>
              <span className='tooltiptext'>Plugin successfully installed</span>
              </div>
            )}
            <p className="currentstate">
            <img className="svg-badge" src= {`${currentPath}${status_dict[value.development_status][1]}`} title={status_dict[value.development_status][0]} />&nbsp;
            {value.aiida_version && (
              <img
                  className="svg-badge"
                  title={`Compatible with aiida-core ${value.aiida_version}`}
                  src={`https://img.shields.io/badge/AiiDA-${value.aiida_version}-007ec6.svg?logo=${base64Icon}`}
                />
            )}
            {sortOption === 'commits' &&
            <img
                  className="svg-badge"
                  style={{padding:'3px'}}
                  src={`https://img.shields.io/badge/Yearly%20Commits-${value.commits_count}-007ec6.svg`}
                />
            }

            {sortOption === 'release' && value.metadata.release_date &&
            <img
                  className="svg-badge"
                  style={{padding:'3px'}}
                  src={`https://img.shields.io/badge/Recent%20Release-${value.metadata.release_date.replace(/-/g, '/')}-007ec6.svg`}
                />
          }
            </p>

            <p>{value.metadata.description}</p>
            <ul className="plugin-info">
              <li>
            <a href={value.code_home}>Source Code</a>
              </li>
            {value.documentation_url && (
              <li>
              <a href={value.documentation_url}>Documentation</a>
              </li>
            )}
            <li>
            <Link to={`/${key}`}>Plugin details</Link>
            </li>

            </ul>

            {value.summaryinfo && (
              <>
                <p className="summaryinfo">
                {value.summaryinfo.map((summaryinfoelem) => (
                  <span className="badge" key={summaryinfoelem.text}>
                    <span className={`badge-left ${summaryinfoelem.colorclass}`}>
                      {summaryinfoelem.text}
                    </span>
                    <span className="badge-right">{summaryinfoelem.count}</span>
                  </span>
                ))}
                </p>
              </>
            )}

          </div>
        ))}
      </div>
      </main>
    );
  }

export default MainIndex
