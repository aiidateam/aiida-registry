import { Route, Routes } from 'react-router-dom';
import { useParams } from 'react-router-dom';
import Logo from './assets/logo.svg'
import whiteLogo from './assets/logo-white-text.svg'
import MARVEL from './assets/MARVEL.png'
import MaX from './assets/MaX.png'
import './App.css'
import Box from '@mui/material/Box';

import MainIndex from './Components/MainIndex'
import Details from './Components/Details'
import Sidebar from './Components/Sidebar';

function App() {

  return (
    <>
    <Header />
    <div id='app-body'>
      <Routes>
        <Route path="/" element={<MainIndex />} />
        <Route path="/:key" element={<DetailsContainer />} />
      </Routes>
    </div>
    <Footer />
    </>
  );
}

function Header() {
  return (
      <header id="entrytitle" style={{ backgroundColor: 'black', display: 'block', margin: '0', position:'sticky', top:'0', zIndex:'999', width:'100%', padding: '5px 0px 34px 0px' }}>
        <h1>
          <a href="http://aiidateam.github.io/aiida-registry"><img src={whiteLogo} height="70px" /></a>
        </h1>
        <p style={{ fontSize: '90%' }}>
          <a href="http://github.com/aiidateam/aiida-registry" style={{ color: '#999' }}>[View on GitHub/register your package]</a>
        </p>
      </header>
  )
}

function Footer() {
  return (
        <footer  className="footer">
          <hr />
          The official <a href="http://aiidateam.github.io/aiida-registry">registry</a> of <a href="http://www.aiida.net">AiiDA</a> plugins.
          <br />
          This work is supported by the <a href="http://nccr-marvel.ch" target="_blank">MARVEL National Centre for Competence in Research</a> funded by the <a href="http://www.snf.ch/en" target="_blank">Swiss National Science Foundation</a>, as well as by the <a href="http://www.max-centre.eu" target="_blank">MaX European Centre of Excellence</a> funded by the Horizon 2020 EINFRA-5 program, Grant No. 676598.
          <br /><br />

          <div style={{ textAlign: 'center' }}>
            <img src={MARVEL} height="70px" />&nbsp;&nbsp;&nbsp;&nbsp;<img src={MaX} height="70px" />
          </div>
        </footer>
  )
}


/**
 * DetailsContainer component displays the details of a specific plugin identified by the key parameter.
 * It renders the Details component on the left side and the Sidebar component on the right side.
 *
 * @component
 * @example
 * // Render DetailsContainer with a specific plugin key:
 * <DetailsContainer />
 *
 * @returns {JSX.Element} JSX element representing the DetailsContainer.
 */

function DetailsContainer() {
  const { key } = useParams();

  return (
      <>
      <div style={{display:'flex'}}>
          <Details pluginKey={key} />
          <Sidebar pluginKey={key} />
          </div>
      </>
  );
}

export default App;
