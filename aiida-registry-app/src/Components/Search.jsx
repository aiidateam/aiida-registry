import { Link } from 'react-router-dom';
import jsonData from '../plugins_metadata.json'
import './Search.css'
import SearchIcon from '@mui/icons-material/Search';
import KeyboardReturnIcon from '@mui/icons-material/KeyboardReturn';
import Fuse from 'fuse.js'

import { useSearchContext } from '../Contexts/SearchContext';
import { extractSentenceAroundKeyword } from './utils'

const plugins  = jsonData["plugins"]

let ep_keys = [ 'name', 'metadata.description', 'entry_point_prefix', 'metadata.author']

/**
 * Process the plugins object to prepare it for search by:
 * - Converting the object to a list of plugins.
 * - Stringifying the entry points object for search index compatibility.
 * @param {Object} plugins - The plugins object containing entry points.
 * @returns {Object} instance of fuse search index of plugins.
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

    //Create a fuse instance for searching the provided keys.
    const fuse = new Fuse(pluginsList, {
        keys: ep_keys,
        includeScore: true,
        ignoreLocation: true,
        threshold: 0.1,
        includeMatches: true,
      })

    return fuse;
}

const fuse = preparePluginsForSearch(plugins);

/**
 * Display a search box.
 * Display suggestions list as user type a search query.
 * @returns {JSX.Element}
 */
export function Search() {
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

  //Example of fuse search results output:
  //https://github.com/krisk/Fuse/blob/main/docs/examples.md#nested-search
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

/**
 * Display the search results page.
 * @returns {JSX.Element}
 */
export function SearchResults () {
    const { searchResults, searchQuery } = useSearchContext();

    return (
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
    );
}

/**
 * Display a short sentence that matches the search with the search query highlighted in yellow.
 * @param {String} match_value The matched entry point.
 * @returns {JSX.Element}
 */
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
