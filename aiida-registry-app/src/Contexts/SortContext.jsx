import { useState, createContext, useContext } from 'react';
import jsonData from '../plugins_metadata.json'

const plugins  = jsonData["plugins"]

const SortContext = createContext();

export const useSortContext = () => useContext(SortContext);

export const SortContextProvider = ({ children }) => {
  const [sortOption, setSortOption] = useState('commits'); //Available options: 'commits', 'release', and 'alpha'.
  const [sortedData, setSortedData] = useState(plugins);
  return (
    <SortContext.Provider value={{ sortOption, setSortOption, sortedData, setSortedData }}>
      {children}
    </SortContext.Provider>
  );
};
