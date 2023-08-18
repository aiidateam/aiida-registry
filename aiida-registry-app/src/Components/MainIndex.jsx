import { useState, createContext, useContext, useEffect } from 'react';
import { Link } from 'react-router-dom';
import jsonData from '../plugins_metadata.json'
import base64Icon from '../base64Icon';
import Box from '@mui/material/Box';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import SearchIcon from '@mui/icons-material/Search';
import Fuse from 'fuse.js'
const globalsummary = jsonData["globalsummary"]
const plugins  = jsonData["plugins"]
const status_dict = jsonData["status_dict"]
const length = Object.keys(plugins).length;
const currentPath = import.meta.env.VITE_PR_PREVIEW_PATH || "/aiida-registry/";


//The search context enables accessing the search query and the plugins data among different components.
const SearchContext = createContext();

const useSearchContext = () => useContext(SearchContext);

export const SearchContextProvider = ({ children }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [sortedData, setSortedData] = useState(plugins);
  return (
    <SearchContext.Provider value={{ searchQuery, setSearchQuery, sortedData, setSortedData}}>
      {children}
    </SearchContext.Provider>
  );
};

/**
 * Process the plugins object to prepare it for search by:
 * - Converting the object to a list of plugins.
 * - Stringifying the entry points object for search index compatibility.
 * @param {object} plugins - The plugins object containing entry points.
 * @returns {Array} List of plugins ready for search.
 */
function preparePluginsForSearch(plugins) {
  const pluginsList = [];
  const clonedPlugins = JSON.parse(JSON.stringify(plugins));

  Object.entries(clonedPlugins).forEach(([key, pluginData]) => {
    pluginData.entry_points = JSON.stringify(pluginData.entry_points);
    pluginsList.push(pluginData);
  });

  return pluginsList;
}

const pluginsListForSearch = preparePluginsForSearch(plugins);

function Search() {
  const { searchQuery, setSearchQuery, sortedData, setSortedData } = useSearchContext();
  // Update searchQuery when input changes
  const handleSearch = (searchQuery) => {
    setSearchQuery(searchQuery);
    if (searchQuery == "") {
      setSortedData(plugins)
    }
    document.querySelector(".suggestions-list").style.display = "block";
  }
  //Create a fuce instance for searching the provided keys.
  const fuse = new Fuse(pluginsListForSearch, {
    keys: [ 'name', 'metadata.description', 'entry_point_prefix', 'metadata.author', 'entry_points'],
    includeScore: true,
    ignoreLocation: true,
    threshold: 0.1
  })
  let searchRes = fuse.search(searchQuery)
  const suggestions = searchRes.map((item) => item.item.name); //get the list searched plugins
  const resultObject = {};

  //Convert the search results array to object
  searchRes.forEach(item => {
    resultObject[item.item.name] = plugins[item.item.name];
  });

  //Update the sortedData state with the search results
  const handleSubmit = (e) => {
    e.preventDefault();
    if (searchQuery) {
    setSortedData(resultObject);
    document.querySelector(".suggestions-list").style.display = "none";
    }
  };

  //return the suggestions list
  return (
    <>
    <div className="search">
      <form className="search-form">
        <button style={{fontSize:'20px', minWidth:'90px', backgroundColor:'white', border: '1px solid #ccc', borderRadius: '4px'}} onClick={(e) => {handleSubmit(e);}}><SearchIcon /></button>
        <input type="text" placeholder="Search for plugins" value={searchQuery} label = "search" onChange={(e) => handleSearch(e.target.value)} />
      </form>
    {/* Display the list of suggestions */}
    <ul className="suggestions-list">
        {suggestions.map((suggestion) => (
          <Link to={`/${suggestion}`}><li key={suggestion} className="suggestion-item">
            {suggestion}
          </li></Link>
        ))}
      </ul>
      </div>
    </>
  )
}


export function MainIndex() {
    const { searchQuery, setSearchQuery, sortedData, setSortedData } = useSearchContext();
    const [sortOption, setSortOption] = useState('commits'); //Available options: 'commits', 'release', and 'alpha'.

    useEffect(() => {
      document.documentElement.style.scrollBehavior = 'auto';
      handleSort(sortOption);
      setupScrollBehavior();
    }, [sortOption]);

    function sortByCommits(plugins) {
      const pluginsArray = Object.entries(plugins);
      // Sort the array based on the commit_count value
      pluginsArray.sort(([, pluginA], [, pluginB]) => pluginB.commits_count - pluginA.commits_count);
      // Return a new object with the sorted entries
      return Object.fromEntries(pluginsArray);
    }

    function sortByRelease(plugins) {
      //Sort plugins by the recent release date, the newer the release date the larger the value,
      //and the higher ranking it get. Sorting in descending order by date.
      const pluginsArray = Object.entries(plugins);
      pluginsArray.sort(([, pluginA], [, pluginB]) => {
        if (!pluginA.metadata.release_date && !pluginB.metadata.release_date) {
         return 0; // Both plugins have no release date, keep them in the current order
        } else if (!pluginA.metadata.release_date) {
          return 1; // Only pluginB has a release date, put pluginB higher ranking than pluginA.
        } else if (!pluginB.metadata.release_date) {
          return -1; // Only pluginA has a release date, put pluginA higher ranking than pluginB.
        } else {
          return new Date(pluginB.metadata.release_date) - new Date(pluginA.metadata.release_date);
        }
      });

      //Return a new object with the sorted entries
      return Object.fromEntries(pluginsArray);
  }

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

    const handleSort = (option) => {
      setSortOption(option);


      let sortedPlugins = {};
      if (option === 'commits') {
        sortedPlugins = sortByCommits(plugins);
      }
      else if (option == 'alpha') {
        sortedPlugins = plugins;
      }
      else if (option == 'release') {
        sortedPlugins = sortByRelease(plugins);
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
        <h1>
          Package list
      </h1>
        <div style={{display:'flex', flexDirection:'row', margin:'0 2%'}}>
      <div style={{ flex:'1', marginRight:'10px'}}>
        <Search />
        </div>
          <Box >
            <FormControl >
              <InputLabel id="demo-simple-select-label">Sort</InputLabel>
              <Select
                value={sortOption} label = "Sort" onChange={(e) => handleSort(e.target.value)}
              >
                <MenuItem value='commits'>Commits Count</MenuItem>
                <MenuItem value= 'alpha'>Alphabetical</MenuItem>
                <MenuItem value='release'>Recent Release</MenuItem>
              </Select>
            </FormControl>
          </Box>
          </div>

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
