import jsonData from '../plugins_metadata.json'
import './MainIndex.css'

import { Search, SearchResults } from './Search';
import { Sort } from './Sort';
import { PluginsList } from './PluginsList';
import { useSearchContext } from '../Contexts/SearchContext';

const globalsummary = jsonData["globalsummary"]
const plugins  = jsonData["plugins"]
const length = Object.keys(plugins).length;

/**
 * Displays a summary of statistics for all registered plugin packages.
 *
 * This component renders a summary section showing statistics about the registered plugin packages,
 * including the total number of packages and plugins in each package. It provides a visual representation
 * of these statistics using colored badges.
 * @returns {JSX.Element}
 */
function GlobalSummary() {

  return (
    <>
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
    </>
  );
}


export function MainIndex() {
    const { isSearchSubmitted } = useSearchContext();

    return (
      <main className='fade-enter'>
        <GlobalSummary />
      <div id='entrylist'>
        <h1>
          Package list
      </h1>
      <div className='bar-container'>
        <div style={{ flex:'1', marginRight:'10px'}}>
        <Search />
        </div>
        <Sort />
      </div>

          {isSearchSubmitted === true ? (
            <SearchResults />
        ):(
          <PluginsList />
        )}
      </div>
      </main>
    );
  }
