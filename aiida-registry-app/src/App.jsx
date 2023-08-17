import { useState } from 'react';
import { Link, Route, Routes } from 'react-router-dom';
import { useParams } from 'react-router-dom';
import Logo from './assets/logo.svg'
import whiteLogo from './assets/logo-white-text.svg'
import MARVEL from './assets/MARVEL.png'
import MaX from './assets/MaX.png'
import './App.css'
import jsonData from './plugins_metadata.json'
import base64Icon from './base64Icon';



const entrypointtypes = jsonData["entrypointtypes"]
const globalsummary = jsonData["globalsummary"]
const plugins  = jsonData["plugins"]
const status_dict = jsonData["status_dict"]
const length = Object.keys(plugins).length;
const currentPath = window.location.pathname;
function App() {
  console.log(currentPath);

  return (
    <>
    <header id="entrytitle" style={{ backgroundColor: '#000', margin: '0', padding: '5px 20px 25px 20px' }}>
      <h1>
        <a href="http://aiidateam.github.io/aiida-registry"><img src={whiteLogo} height="70px" /></a>
      </h1>
      <p style={{ fontSize: '90%' }}>
        <a href="http://github.com/aiidateam/aiida-registry" style={{ color: '#999' }}>[View on GitHub/register your package]</a>
      </p>
    </header>

    <div id='app-body'>
      <Routes>
        <Route path="/" element={<MainIndex />} />
        <Route path="/:key" element={<Details />} />
      </Routes>
    </div>
    <footer className="footer">
      <hr />
      The official <a href="http://aiidateam.github.io/aiida-registry">registry</a> of <a href="http://www.aiida.net">AiiDA</a> plugins.
      <br />
      This work is supported by the <a href="http://nccr-marvel.ch" target="_blank">MARVEL National Centre for Competence in Research</a> funded by the <a href="http://www.snf.ch/en" target="_blank">Swiss National Science Foundation</a>, as well as by the <a href="http://www.max-centre.eu" target="_blank">MaX European Centre of Excellence</a> funded by the Horizon 2020 EINFRA-5 program, Grant No. 676598.
      <br /><br />

      <div style={{ textAlign: 'center' }}>
        <img src={MARVEL} height="70px" />&nbsp;&nbsp;&nbsp;&nbsp;<img src={MaX} height="70px" />
      </div>
    </footer>
    </>
  );
}

function MainIndex() {
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
        Package list (alphabetical order)
    </h1>
      {Object.entries(plugins).map(([key, value]) => (
        <div className='submenu-entry' key={key}>
          <Link to={`/${key}`}><h2>{key}</h2></Link>
          <p className="currentstate">
          <img className="svg-badge" src= {`${currentPath}${status_dict[value.development_status][1]}`} title={status_dict[value.development_status][0]} />&nbsp;
          {value.aiida_version && (
            <img
                className="svg-badge"
                title={`Compatible with aiida-core ${value.aiida_version}`}
                src={`https://img.shields.io/badge/AiiDA-${value.aiida_version}-007ec6.svg?logo=${base64Icon}`}
              />
          )}

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
          <a href={`/${key}`}>Plugin details</a>
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
    </div>
    </main>
  );
}

function Details() {
  const { key } = useParams();
  const value = plugins[key];
  window.scrollTo(0, 0);

  return (
    <>
    <div id="details" className='fade-enter'>
    <h1 className='plugin-header'>
        AiiDA plugin package &quot;<a href={value.code_home}>{value.name}</a>&quot;
    </h1>
    <Link to={'/'}><p>&lt; back to the registry index</p></Link>
    <h2>General information</h2>
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

    <h2>Detailed information</h2>
      {Object.keys(value.metadata).length !== 0 ? (
        <>
          <p>
            <strong>Author(s)</strong>: {value.metadata.author}
          </p>
          {value.metadata.author_email && (
            <p>
              <strong>Contact</strong>:{" "}
              <a href={`mailto:${value.metadata.author_email}`}>
                {value.metadata.author_email}
              </a>
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
              <h3>Plugins provided by the package</h3>
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
              <div key={entrypointtype}>
                <h4>
                  {entrypointtype in entrypointtypes ? (
                    <>
                      {entrypointtypes[entrypointtype]}{" "}
                      <span className="entrypointraw">({entrypointtype})</span>
                    </>
                  ) : (
                    entrypointtype
                  )}
                </h4>
                <ul>
                  {Object.entries(entrypointlist).map(([ep_name, ep_module]) => (
                    <li key={ep_name}>
                      <code>{ep_name} </code>
                      <div className="classbox">
                        class
                        <span className="tooltiptext"> {ep_module}</span>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
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

export default App;
