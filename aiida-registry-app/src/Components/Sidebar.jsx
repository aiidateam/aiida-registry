import jsonData from '../plugins_metadata.json'
import Divider from '@mui/material/Divider';
import Drawer from '@mui/material/Drawer';

const plugins  = jsonData["plugins"]
const sidebarWidth = 340;

/**
 * Sidebar component displays a sidebar with navigation links related to a specific plugin identified by the pluginKey prop.
 * The sidebar includes links to general and detailed information about the plugin.
 * If the plugin contains entry points, it will display links to those entry points as well.
 *
 * @component
 * @param {string} pluginKey - The key of the plugin to display in the sidebar.
 * @returns {JSX.Element} JSX element representing the Sidebar component.
 */
function Sidebar({pluginKey}){
  const value = plugins[pluginKey]
  function handleClick() {
    function hideHeader(){
    document.querySelector("header").style.top = "-155px";
    document.querySelector("#sidebar .MuiDrawer-paper").style.marginTop = '0';
    }
    setTimeout(hideHeader, 800)
  };
  const sidebar = (
    <div style={{paddingLeft: '10px'}}>
      <h1>Plugin content</h1>
      <Divider />
      <p><a style={{color:'black'}} href='#general.information' onClick={handleClick}>General Information</a></p>
      <p><a style={{color:'black'}} href='#detailed.information' onClick={handleClick}>Detailed Information</a></p>
      <p><a style={{color:'black'}} href='#plugins' onClick={handleClick}>Plugins provided by the package</a></p>
      {value.entry_points && (
                Object.entries(value.entry_points).map(([entrypointtype, entrypointlist]) => (
                  <>
                    <ul>
                      <li>
                        <a style={{color:'black'}} href={`#${entrypointtype}`} onClick={handleClick}>{entrypointtype}</a>
                        {Object.entries(entrypointlist).map(([ep_name, ep_module]) => (
                          <ul key={ep_name}>
                            <li>
                              <a style={{color:'black'}} href={`#${entrypointtype}.${ep_name}`} onClick={handleClick}>{ep_name}</a>
                            </li>
                          </ul>
                        ))}
                      </li>
                    </ul>
                  </>
                ))
          )}
      <Divider />

    </div>
  );
  return (
    <Drawer
          variant="permanent"
          id='sidebar'
          anchor="right"
            sx={{
              display: { xs: 'none', sm: 'block' }, //This disables the sidebar for small screens(mobile phones).
          }}
            open
          >
            {sidebar}
          </Drawer>
  )
}

export default Sidebar;
