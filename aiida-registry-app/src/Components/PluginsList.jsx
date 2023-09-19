import { Link } from 'react-router-dom';
import { useState } from 'react';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import Dialog from '@mui/material/Dialog';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';

import jsonData from '../plugins_metadata.json'
import base64Icon from '../base64Icon';
import './PluginsList.css'

import { useSortContext } from '../Contexts/SortContext';

const status_dict = jsonData["status_dict"]
const currentPath = import.meta.env.VITE_PR_PREVIEW_PATH || "/aiida-registry/";

/**
 * Renders a list of plugins sorted according to the specified criteria.
 *
 * @component
 * @returns {JSX.Element} A component rendering a list of plugins sorted based on the selected criteria.
 */
export function PluginsList() {
    const { sortOption, sortedData } = useSortContext();

    return (
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
              <a rel='noopener noreferrer'  target='_blank' href='https://hub.docker.com/r/aiidateam/aiida-core'><code> aiida-core</code> docker image</a>.
              For in-depth compatibility tests see the source code repository of the plugin.
            </DialogContentText>
          </DialogContent>
        </Dialog>
      </>
    );
}
