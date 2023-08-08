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

  const sidebar = (
    <div style={{paddingLeft: '10px'}}>
      <h1>Plugin content</h1>
      <Divider />
      <p><a style={{color:'black'}} href='#general.information'>General Information</a></p>
      <p><a style={{color:'black'}} href='#detailed.information'>Detailed Information</a></p>
      <p><a style={{color:'black'}} href='#plugins'>Plugins provided by the package</a></p>
      {value.entry_points && (
                Object.entries(value.entry_points).map(([entrypointtype, entrypointlist]) => (
                  <>
                    <ul>
                      <li>
                        <a style={{color:'black'}} href={`#${entrypointtype}`}>{entrypointtype}</a>
                        {Object.entries(entrypointlist).map(([ep_name, ep_module]) => (
                          <ul key={ep_name}>
                            <li>
                              <a style={{color:'black'}} href={`#${entrypointtype}.${ep_name}`}>{ep_name}</a>
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
          anchor="right"
            sx={{
              display: { xs: 'none', sm: 'block' }, //This disables the sidebar for small screens(mobile phones).
              '& .MuiDrawer-paper': {
                boxSizing: 'border-box',
                width: sidebarWidth,
                maxHeight:'calc(100vh - 11rem)', //Set the height to be under the header
                mt:22,
                backgroundColor:'lightgray',

            }
          }}
            open
          >
            {sidebar}
          </Drawer>
  )
}

export default Sidebar;