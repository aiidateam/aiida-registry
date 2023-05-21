import { useState } from 'react';
import { Link, Route, Routes } from 'react-router-dom';
import { useParams } from 'react-router-dom';
import Logo from './assets/logo.svg'
import whiteLogo from './assets/logo-white-text.svg'
import MARVEL from './assets/MARVEL.png'
import MaX from './assets/MaX.png'
import './App.css'
import jsonData from './plugins_metadata.json'



const entrypointtypes = jsonData["entrypointtypes"]
const globalsummary = jsonData["globalsummary"]
const plugins  = jsonData["plugins"]
const status_dict = jsonData["status_dict"]
const length = Object.keys(plugins).length;

function App() {

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
        <Route path="/aiida-registry/" element={<MainIndex />} />
        <Route path="/aiida-registry/:key" element={<Details />} />
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
          <Link to={`/aiida-registry/${key}`}><h2>{key}</h2></Link>
          <p className="currentstate">
          <img className="svg-badge" src= {`/aiida-registry/${status_dict[value.development_status][1]}`} title={status_dict[value.development_status][0]} />
          {value.aiida_version && (
            <img
                className="svg-badge"
                title={`Compatible with aiida-core ${value.aiida_version}`}
                src={`https://img.shields.io/badge/AiiDA-${value.aiida_version}-007ec6.svg?logo=data%3Aimage%2Fpng%3Bbase64%2CiVBORw0KGgoAAAANSUhEUgAAACMAAAAhCAYAAABTERJSAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAFhgAABYYBG6Yz4AAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAUbSURBVFiFzZhrbFRVEMd%2Fc%2B5uu6UUbIFC%2FUAUVEQCLbQJBIiBDyiImJiIhmohYNCkqJAQxASLF8tDgYRHBLXRhIcKNtFEhVDgAxBJqgmVh4JEKg3EIn2QYqBlt917xg%2BFss%2ByaDHOtzsz5z%2B%2FuZl7ztmF%2F5HJvxVQN6cPYX8%2FPLnOmsvNAvqfwuib%2FbNIk9cQeQnLcKRL5xLIV%2Fic9eJeunjPYbRs4FjQSpTB3aS1IpRKeeOOewajy%2FKKEO8Q0DuVdKy8IqsbPulxGHUfCBBu%2BwUYGuFuBTK7wQnht6PEbf4tlRomVRjCbXNjQEB0AyrFQOL5ENIJm7dTLZE6DPJCnEtFZVXDLny%2B4Sjv0PmmYu1ZdUek9RiMgoDmJ8V0L7XJqsZ3UW8YsBOwEeHeeFce7jEYXBy0m9m4BbXqSj2%2Bxnkg26MCVrN6DEZcwggtd8pTFx%2Fh3B9B50YLaFOPwXQKUt0tBLegtSomfBlfY13PwijbEnhztGzgJsK5h9W9qeWwBqjvyhB2iBs1Qz0AU974DciRGO8CVN8AJhAeMAdA3KbrKEtvxhsI%2B9emWiJlGBEU680Cfk%2BSsVqXZvcFYGXjF8ABVJ%2BTNfVXehyms1zzn1gmIOxLEB6E31%2FWBe5rnCarmo7elf7dJEeaLh80GasliI5F6Q9cAz1GY1OJVNDxTzQTw7iY%2FHEZRQY7xqJ9RU2LFe%2FYqakdP911ha0XhjjiTVAkDwgatWfCGeYocx8M3glG8g8EXhSrLrHnEFJ5Ymow%2FkhIYv6ttYUW1iFmEqqxdVoUs9FmsDYSqmtmJh3Cl1%2BVtl2s7owDUdocR5bceiyoSivGTT5vzpbzL1uoBpmcAAQgW7ArnKD9ng9rc%2BNgrobSNwpSkkhcRN%2BvmXLjIsDovYHHEfmsYFygPAnIDEQrQPzJYCOaLHLUfIt7Oq0LJn9fxkSgNCb1qEIQ5UKgT%2Fs6gJmVOOroJhQBXVqw118QtWLdyUxEP45sUpSzqP7RDdFYMyB9UReMiF1MzPwoUqHt8hjGFFeP5wZAbZ%2F0%2BcAtAAcji6LeSq%2FMYiAvSsdw3GtrfVSVFUBbIhwRWYR7yOcr%2FBi%2FB1MSJZ16JlgH1AGM3EO2QnmMyrSbTSiACgFBv4yCUapZkt9qwWVL7aeOyHvArJjm8%2Fz9BhdI4XcZgz2%2FvRALosjsk1ODOyMcJn9%2FYI6IrkS5vxMGdUwou2YKfyVqJpn5t9aNs3gbQMbdbkxnGdsr4bTHm2AxWo9yNZK4PXR3uzhAh%2BM0AZejnCrGdy0UvJxl0oMKgWSLR%2B1LH2aE9ViejiFs%2BXn6bTjng3MlIhJ1I1TkuLdg6OcAbD7Xx%2Bc3y9TrWAiSHqVkbZ2v9ilCo6s4AjwZCzFyD9mOL305nV9aonvsQeT2L0gVk4OwOJqXXVRW7naaxswDKVdlYLyMXAnntteYmws2xcVVZzq%2BtHPAooQggmJkc6TLSusOiL4RKgwzzYU1iFQgiUBA1H7E8yPau%2BZl9P7AblVNebtHqTgxLfRqrNvZWjsHZFuqMqKcDWdlFjF7UGvX8Jn24DyEAykJwNcdg0OvJ4p5pQ9tV6SMlP4A0PNh8aYze1ArROyUNTNouy8tNF3Rt0CSXb6bRFl4%2FIfQzNMjaE9WwpYOWQnOdEF%2BTdJNO0iFh7%2BI0kfORzQZb6P2kymS9oTxzBiM9rUqLWr1WE5G6ODhycQd%2FUnNVeMbcH68hYkGycNoUNWc8fxaxfwhDbHpfwM5oeTY7rUX8QAAAABJRU5ErkJggg%3D%3D`}
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
          <a href={`/aiida-registry/${key}`}>Plugin details</a>
          </li>

          </ul>

          {value.summaryinfo && (
            <>
              <p class="summaryinfo">
              {value.summaryinfo.map((summaryinfoelem) => (
                <span className="badge">
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
    <h2>
        AiiDA plugin package &quot;<a href={value.code_home}>{value.name}</a>&quot;
    </h2>
    <Link to={'/aiida-registry/'}><p><a>&lt; back to the registry index</a></p></Link>
    <h2>General information</h2>
    <div>
      <p>
            Current state:
            <img className="svg-badge" src= {`/aiida-registry/${status_dict[value.development_status][1]}`} title={status_dict[value.development_status][0]} />
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
              src={`https://img.shields.io/badge/AiiDA-${value.aiida_version}-007ec6.svg?logo=data%3Aimage%2Fpng%3Bbase64%2CiVBORw0KGgoAAAANSUhEUgAAACMAAAAhCAYAAABTERJSAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAFhgAABYYBG6Yz4AAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAUbSURBVFiFzZhrbFRVEMd%2Fc%2B5uu6UUbIFC%2FUAUVEQCLbQJBIiBDyiImJiIhmohYNCkqJAQxASLF8tDgYRHBLXRhIcKNtFEhVDgAxBJqgmVh4JEKg3EIn2QYqBlt917xg%2BFss%2ByaDHOtzsz5z%2B%2FuZl7ztmF%2F5HJvxVQN6cPYX8%2FPLnOmsvNAvqfwuib%2FbNIk9cQeQnLcKRL5xLIV%2Fic9eJeunjPYbRs4FjQSpTB3aS1IpRKeeOOewajy%2FKKEO8Q0DuVdKy8IqsbPulxGHUfCBBu%2BwUYGuFuBTK7wQnht6PEbf4tlRomVRjCbXNjQEB0AyrFQOL5ENIJm7dTLZE6DPJCnEtFZVXDLny%2B4Sjv0PmmYu1ZdUek9RiMgoDmJ8V0L7XJqsZ3UW8YsBOwEeHeeFce7jEYXBy0m9m4BbXqSj2%2Bxnkg26MCVrN6DEZcwggtd8pTFx%2Fh3B9B50YLaFOPwXQKUt0tBLegtSomfBlfY13PwijbEnhztGzgJsK5h9W9qeWwBqjvyhB2iBs1Qz0AU974DciRGO8CVN8AJhAeMAdA3KbrKEtvxhsI%2B9emWiJlGBEU680Cfk%2BSsVqXZvcFYGXjF8ABVJ%2BTNfVXehyms1zzn1gmIOxLEB6E31%2FWBe5rnCarmo7elf7dJEeaLh80GasliI5F6Q9cAz1GY1OJVNDxTzQTw7iY%2FHEZRQY7xqJ9RU2LFe%2FYqakdP911ha0XhjjiTVAkDwgatWfCGeYocx8M3glG8g8EXhSrLrHnEFJ5Ymow%2FkhIYv6ttYUW1iFmEqqxdVoUs9FmsDYSqmtmJh3Cl1%2BVtl2s7owDUdocR5bceiyoSivGTT5vzpbzL1uoBpmcAAQgW7ArnKD9ng9rc%2BNgrobSNwpSkkhcRN%2BvmXLjIsDovYHHEfmsYFygPAnIDEQrQPzJYCOaLHLUfIt7Oq0LJn9fxkSgNCb1qEIQ5UKgT%2Fs6gJmVOOroJhQBXVqw118QtWLdyUxEP45sUpSzqP7RDdFYMyB9UReMiF1MzPwoUqHt8hjGFFeP5wZAbZ%2F0%2BcAtAAcji6LeSq%2FMYiAvSsdw3GtrfVSVFUBbIhwRWYR7yOcr%2FBi%2FB1MSJZ16JlgH1AGM3EO2QnmMyrSbTSiACgFBv4yCUapZkt9qwWVL7aeOyHvArJjm8%2Fz9BhdI4XcZgz2%2FvRALosjsk1ODOyMcJn9%2FYI6IrkS5vxMGdUwou2YKfyVqJpn5t9aNs3gbQMbdbkxnGdsr4bTHm2AxWo9yNZK4PXR3uzhAh%2BM0AZejnCrGdy0UvJxl0oMKgWSLR%2B1LH2aE9ViejiFs%2BXn6bTjng3MlIhJ1I1TkuLdg6OcAbD7Xx%2Bc3y9TrWAiSHqVkbZ2v9ilCo6s4AjwZCzFyD9mOL305nV9aonvsQeT2L0gVk4OwOJqXXVRW7naaxswDKVdlYLyMXAnntteYmws2xcVVZzq%2BtHPAooQggmJkc6TLSusOiL4RKgwzzYU1iFQgiUBA1H7E8yPau%2BZl9P7AblVNebtHqTgxLfRqrNvZWjsHZFuqMqKcDWdlFjF7UGvX8Jn24DyEAykJwNcdg0OvJ4p5pQ9tV6SMlP4A0PNh8aYze1ArROyUNTNouy8tNF3Rt0CSXb6bRFl4%2FIfQzNMjaE9WwpYOWQnOdEF%2BTdJNO0iFh7%2BI0kfORzQZb6P2kymS9oTxzBiM9rUqLWr1WE5G6ODhycQd%2FUnNVeMbcH68hYkGycNoUNWc8fxaxfwhDbHpfwM5oeTY7rUX8QAAAABJRU5ErkJggg%3D%3D`}
            />
          </p>
          )}

          {value.summaryinfo.length !== 0 && (
            <>
              <h3>Plugins provided by the package</h3>
              {value.summaryinfo.map((summaryinfoelem) => (
                <span className="badge">
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
                      <code>{ep_name}</code>
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
