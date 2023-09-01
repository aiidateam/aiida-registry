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
import Dialog from '@mui/material/Dialog';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import KeyboardReturnIcon from '@mui/icons-material/KeyboardReturn';

import Fuse from 'fuse.js'
import { extractSentenceAroundKeyword } from './utils'

const globalsummary = jsonData["globalsummary"]
const plugins  = jsonData["plugins"]
const status_dict = jsonData["status_dict"]
const length = Object.keys(plugins).length;
const currentPath = import.meta.env.VITE_PR_PREVIEW_PATH || "/aiida-registry/";


//The search context enables accessing the search query, search status, and search results among different components.
const SearchContext = createContext();

const useSearchContext = () => useContext(SearchContext);

export const SearchContextProvider = ({ children }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState();
  const [isSearchSubmitted, setIsSearchSubmitted] = useState(false);
  return (
    <SearchContext.Provider value={{ searchQuery, setSearchQuery, searchResults, setSearchResults, isSearchSubmitted, setIsSearchSubmitted }}>
      {children}
    </SearchContext.Provider>
  );
};
let ep_keys = [ 'name', 'metadata.description', 'entry_point_prefix', 'metadata.author']

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
    Object.entries(pluginData.entry_points).forEach(([key, entry_points]) => {
      for (const k in entry_points) {
        let ep_entries = ['entry_points', key, k]
        pluginData.entry_points[key][k] = JSON.stringify(pluginData.entry_points[key][k]);
        ep_keys.push(ep_entries);
      }
    });
    pluginsList.push(pluginData);
  });

  return pluginsList;
}

const pluginsListForSearch = preparePluginsForSearch(plugins);

function Search() {
  const { searchQuery, setSearchQuery, setSearchResults, isSearchSubmitted, setIsSearchSubmitted } = useSearchContext();
  // Update searchQuery when input changes
  const handleSearch = (searchQuery) => {
    setSearchQuery(searchQuery);
    document.querySelector(".suggestions-list").style.display = "block";
    document.querySelector(".dropdown-search").style.display = "block";
    if (searchQuery == "" || isSearchSubmitted == true) {
      setIsSearchSubmitted(false);
      document.querySelector(".dropdown-search").style.display = "none";
    }
      // Hide the Enter symbol when the input is empty
  const enterSymbol = document.querySelector('.enter-symbol');
  if (enterSymbol) {
    enterSymbol.style.opacity = searchQuery ? '1' : '0';
  }

  }
  //Create a fuce instance for searching the provided keys.
  const fuse = new Fuse(pluginsListForSearch, {
    keys: ep_keys,
    includeScore: true,
    ignoreLocation: true,
    threshold: 0.1,
    includeMatches: true,
  })
  let searchResults = fuse.search(searchQuery)

  //Update the searchResults state with the search results
  const handleSubmit = (e) => {
    e.preventDefault();
    if (searchQuery) {
    setSearchResults(searchResults);
    setIsSearchSubmitted(true);
    document.querySelector(".suggestions-list").style.display = "none";
    document.querySelector(".dropdown-search").style.display = "none";
    }
  };

  //return the suggestions list
  return (
    <>
    <div className="search">
      <form className="search-form">
        <button style={{fontSize:'20px', minWidth:'90px', backgroundColor:'white', border: '1px solid #ccc', borderRadius: '4px'}} onClick={(e) => {handleSubmit(e);}}><SearchIcon /></button>
        <div className='input-container'>
        <input type="text" placeholder="Search for plugins" value={searchQuery} label = "search" onChange={(e) => handleSearch(e.target.value)} />
        <KeyboardReturnIcon className='enter-symbol' />
        </div>
      </form>
    {/* Display the list of suggestions */}
    <ul className="suggestions-list">
    {searchResults.slice(0,3).map((suggestion) => (
        <>
            <Link to={`/${suggestion.item.name}`}><h3 key={suggestion.item.name} className="suggestion-item">
              {suggestion.item.name} </h3></Link>
            <ul>
              {/* Filter by object means to filter the entry points keys where we need to highlight and redirect.
              As entry points keys = ['entry_points', 'ep_group', 'ep_name'] while other keys are strings.
               */}
              {suggestion.matches.filter(match => typeof match.key == 'object').slice(0,1).map((match) => (
                <>
              <Link to={`/${suggestion.item.name}#${match.key[1]}.${match.key[2]}`}><li key={match.key} className="suggestion-item">
                {match.key[2]} </li></Link>
                <SearchResultSnippet match_value={match.value} />
              </>
              ))}
            </ul>
          </>
            ))}
            <button className='dropdown-search' onClick={(e) => {handleSubmit(e);}}> Search</button>
      </ul>
      </div>
    </>
  )
}


export function MainIndex() {
    const { searchQuery, setSearchQuery, searchResults, isSearchSubmitted, setIsSearchSubmitted } = useSearchContext();
    const [sortOption, setSortOption] = useState('commits'); //Available options: 'commits', 'release', and 'alpha'.
    const [sortedData, setSortedData] = useState(plugins);

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
      setSearchQuery('');
      setIsSearchSubmitted(false);


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
        <div className='bar-container'>
      <div style={{ flex:'1', marginRight:'10px'}}>
        <Search />
        </div>
          <Box>
            <FormControl >
              <InputLabel>Sort</InputLabel>
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

          {isSearchSubmitted === true ? (
            <>
            <h2>Showing {searchResults.length} pages matching the search query.</h2>
            {searchResults.length === 0 && (
              <div>
            <h3 className='submenu-entry' style={{textAlign:'center', color:'black'}}>Can't find what you're looking for?<br/>
             Join the AiiDA community on Discourse and request a plugin <a href='https://aiida.discourse.group/new-topic?title=Request%20for%20Plugin...&category=community/plugin-requests' target="_blank">here.</a></h3>
            </div>
            )}
                {searchResults.map((suggestion) => (
                  <>
                <div className='submenu-entry'>
                    <Link to={`/${suggestion.item.name}`}><h3 key={suggestion.item.name} className="suggestion-item">
                      {suggestion.item.name}
                    </h3></Link>
                    <ul>

                    {suggestion.matches.filter(match => typeof match.key == 'object').map((match) => (
                      <>
                    <Link to={`/${suggestion.item.name}#${match.key[1]}.${match.key[2]}`}><li key={match.key} className="suggestion-item">
                      {match.key[2]}
                    </li></Link>
                    <SearchResultSnippet match_value={match.value} />
                    </>
                    ))}
                </ul>
                    </div>
                    </>
                  ))}
            </>

        ):(
          <>
        {Object.entries(sortedData).map(([key, value]) => (
          <div className='submenu-entry' key={key}>
            <Link to={`/${key}`}><h2 style={{display:'inline'}}>{key} </h2></Link>
            {value.is_installable === "True" && (
              <CheckMark />
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
        </>
        )}
      </div>
      </main>
    );
  }

  function CheckMark() {
    const [open, setOpen] = useState(false);

    const handleClickOpen = () => {
      setOpen(true);
    };

    const handleClose = () => {
      setOpen(false);
    };

    return (
      <>
        <div className='classbox' style={{backgroundColor:'transparent'}}>
          <CheckCircleIcon onClick={handleClickOpen} style={{color:'green', cursor:'pointer', marginBottom:'-5'}}/>
        <span className='tooltiptext'>Plugin successfully installed</span>
        </div>
        <Dialog
          open={open}
          onClose={handleClose}
        >
          <DialogTitle>
            {"This plugin can be installed with the latest aiida-core version."}
          </DialogTitle>
          <DialogContent>
            <DialogContentText>
              This check mark indicates that this plugin was installed successfully inside the latest
              <a href='(https://hub.docker.com/r/aiidateam/aiida-core' target='_blank'><code> aiida-core</code> docker image</a>.
              For in-depth compatibility tests see the source code repository of the plugin.
            </DialogContentText>
          </DialogContent>
        </Dialog>
      </>
    );
  }

function SearchResultSnippet({match_value}) {
  const {searchQuery} = useSearchContext();
  const [before, matchedText, after] = extractSentenceAroundKeyword(match_value, searchQuery);
  return (
    <>
    {before != null && (
      <p>{before}
       <span style={{backgroundColor:'yellow'}}>{matchedText}</span>
      {after}...</p>
    )}
    </>
  )
}