import { useState, createContext, useContext } from 'react';

//The search context enables accessing the search query, search status, and search results among different components.
const SearchContext = createContext();

export const useSearchContext = () => useContext(SearchContext);

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
