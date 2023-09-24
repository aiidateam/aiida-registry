import { Link } from 'react-router-dom';
import Markdown from 'markdown-to-jsx';
import { useEffect } from 'react';

import jsonData from '../plugins_metadata.json'
import './Details.css'
import base64Icon from '../base64Icon';
import Alert from '@mui/material/Alert';

const entrypointtypes = jsonData["entrypointtypes"]
const plugins  = jsonData["plugins"]
const status_dict = jsonData["status_dict"]
const currentPath = import.meta.env.VITE_PR_PREVIEW_PATH || "/aiida-registry/";


function Details({pluginKey}) {
    const value = plugins[pluginKey];
    useEffect(() => {
      window.scrollTo(0, 0);
      document.documentElement.style.scrollBehavior = 'smooth';
      const scrollToAnchor = () => {
        const hash = window.location.hash;

        if (hash) {
          //Add a space to the url and remove it again, this trick allows to scroll to the specified section.
          let cur = window.location.href
          window.location.href = cur+' ';
          window.location.href = cur;
          const targetSection = document.getElementById(hash);
          if (targetSection) {
            targetSection.scrollIntoView();
          }
        }
      };

      scrollToAnchor();
  }, []);
    return (
      <>

      <div id="details" className='fade-enter'>
      <h1 className='plugin-header'>
          AiiDA plugin package &quot;<a href={value.code_home}>{value.name}</a>&quot;
      </h1>
      <Link to={'/'}><p style={{display:'inline'}}>&lt; back to the registry index</p></Link>
      <h2 id='general.information'>General information</h2>
      <div>
        <p>
              <strong>Current state: </strong>
              <img className="svg-badge" src= {`${currentPath}${status_dict[value.development_status][1]}`} title={status_dict[value.development_status][0]} />
        </p>
        {value.metadata.description && (
        <p>
            <strong>Short description</strong>: { value.metadata.description }
        </p>
        )}
        {value.pip_url && (
        <p>
            <strong>How to install</strong>: <code>{value.pip_install_cmd}</code>
        </p>
        )}

        <p>
            <strong>Source code</strong>: <a href={ value.code_home } target="_blank">Go to the source code repository</a>
        </p>
      {value.documentation_url ? (
        <p>
            <strong>Documentation</strong>: <a href={value.documentation_url} target="_blank">Go to plugin documentation</a>
        </p>
      ) : (
        <p>
          <strong>Documentation</strong>: No documentation provided by the package author
        </p>

      )}
      </div>

      <h3>Registry checks</h3>
      {value.warnings || value.errors ? (
        <>
          {value.warnings && (
            <>
            {value.warnings.map((warning) => (
              <Alert severity="warning">{warning}</Alert>
            ))}
            </>
          )}
          {value.errors && (
            <>
          {value.errors.map((error) => (
            <Alert severity="error"><pre>{error}</pre></Alert>
          ))}
            </>
          )}
        </>
      ) : (
        <Alert severity="success">All checks passed!</Alert>
      )}

      <h2 id='detailed.information'>Detailed information</h2>
        {Object.keys(value.metadata).length !== 0 ? (
          <>
            {value.metadata.author && (
              <p>
                <strong>Author(s)</strong>: {value.metadata.author}
              </p>
            )}
            {value.metadata.author_email && (
              <p>
                <strong>Contact</strong>:
                  {value.metadata.author_email.split(',').map(email => (
                    <span key={email}>
                      <a href={`mailto:${email.trim()}`}>{email.trim()}</a>
                      {', '}
                    </span>
                  ))}
              </p>
            )}
            <p>
              <strong>How to use from python</strong>:{" "}
              <code>import {value.package_name}</code>
            </p>
            <p>
              <strong>Most recent version</strong>: {value.metadata.version}
            </p>
            {value.aiida_version && (
            <p>
              <strong>Compatibility: </strong>
              <img
                className="svg-badge"
                src={`https://img.shields.io/badge/AiiDA-${value.aiida_version}-007ec6.svg?logo=${base64Icon}`}
              />
            </p>
            )}

            {value.summaryinfo.length !== 0 && (
              <>
                <h3 id = 'plugins'>Plugins provided by the package</h3>
                {value.summaryinfo.map((summaryinfoelem) => (
                  <span className="badge" key={summaryinfoelem.text}>
                    <span className={`badge-left ${summaryinfoelem.colorclass}`}>
                      {summaryinfoelem.text}
                    </span>
                    <span className="badge-right">{summaryinfoelem.count}</span>
                  </span>
                ))}
              </>
            )}


            {value.entry_points ? (
              Object.entries(value.entry_points).map(([entrypointtype, entrypointlist]) => (
                <>
                <div key={entrypointtype}>
                  <h2 style={{color:'black'}} id={entrypointtype}>
                    {entrypointtype in entrypointtypes ? (
                      <>
                        {entrypointtypes[entrypointtype]}{" "}
                        <span className="entrypointraw">({entrypointtype})</span>
                      </>
                    ) : (
                      entrypointtype
                    )}
                  </h2>
                  <ul>
                    {Object.entries(entrypointlist).map(([ep_name, ep_module]) => (
                      <li key={ep_name}>
                        <h2 style={{color:'black'}} id={`${entrypointtype}.${ep_name}`}>{ep_name}</h2>
                        {typeof ep_module === "string" ? (
                        <div className="classbox">
                          class
                          <span className="tooltiptext"> {ep_module}</span>
                        </div>
                        ) : (
                          <EntryPoints entryPoints={ep_module} />
                        )}
                      </li>
                    ))}
                  </ul>
                </div>
                </>
              ))
            ) : (
              <p>No entry points defined for this plugin.</p>
            )}
          </>
        ) : (
          <div id="description">
            <p>
              Detailed information for this package could not be obtained. Ask the
              plugin author to add a <code>setup.json</code> file to the plugin
              source code.
            </p>
          </div>
        )}
      </div>

      </>
    );
  }

  const EntryPoints = ({entryPoints}) => {
    return (

  <div style={{overflow:'auto'}}>
  <table>
      <tbody>
          <tr>
              <th>Class</th>
              <td><code>{entryPoints.class}</code></td>
          </tr>
      </tbody>
  </table>
  <table>
  <tr>
          <th>Description</th>
      </tr>
        {entryPoints.description.map((description) => (
      <tr className='ep_description'>
          <Markdown>{description.trim()}</Markdown>
      </tr>
        ))}
  </table>

  <table>

      <tr>
          <th>Inputs</th>
          <th>Required</th>
          <th>Valid Types</th>
          <th>Description</th>
      </tr>
      <Specs spec={entryPoints.spec.inputs} />

      <tr>
          <th>Outputs</th>
          <th>Required</th>
          <th>Valid Types</th>
          <th>Description</th>
      </tr>

      <Specs spec={entryPoints.spec.outputs} />

  </table>
  <table>

  <tr>
          <th>Exit Codes</th>
      </tr>
      <tr>
          <th>Status</th>
          <th>Message</th>
      </tr>
      {entryPoints.spec.exit_codes.map((exit_codes) => (
        <tr className='ep_description'>
          <td>{exit_codes.status}</td>
          <Markdown>{exit_codes.message}</Markdown>
        </tr>
      ))}

  </table>
  </div>
    );

  };
  const Specs = ({spec}) => {
    return (
      <>
           {spec.map((inputs) => (
             <tr className='ep_description'>
            <td>{inputs.name}</td>
            <td>{inputs.required.toString()}</td>
            <td>{inputs.valid_types}</td>
            <Markdown>{inputs.info}</Markdown>
          </tr>
        ))}
      </>

    )
  }

export default Details
