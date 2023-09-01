import { useEffect } from 'react';
import Box from '@mui/material/Box';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';

import jsonData from '../plugins_metadata.json'

import { useSortContext } from '../Contexts/SortContext';
import { useSearchContext } from '../Contexts/SearchContext';

const plugins  = jsonData["plugins"]

/**
 * Display a dropdown menu with sort options.
 *
 * Change the plugins sort order based on the selected one.
 * @returns {JSX.Element} A dropdown menu with sort options.
 */
export function Sort() {
    const { setSearchQuery, setIsSearchSubmitted } = useSearchContext();
    const { sortOption, setSortOption, setSortedData } = useSortContext();

    useEffect(() => {
      document.documentElement.style.scrollBehavior = 'auto';
      handleSort(sortOption);
      setupScrollBehavior();
    }, [sortOption]);

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
    );
}
