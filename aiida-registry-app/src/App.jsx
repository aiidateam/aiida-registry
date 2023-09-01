import { Route, Routes } from 'react-router-dom';
import { useParams } from 'react-router-dom';
import whiteLogo from './assets/logo-white-text.svg'
import MARVEL from './assets/MARVEL.png'
import MaX from './assets/MaX.png'
import './App.css'
import { useEffect, createContext, useState, useContext } from 'react';
import { MainIndex } from './Components/MainIndex'
import { SearchContextProvider } from './Contexts/SearchContext';
import { SortContextProvider } from './Contexts/SortContext';
import Details from './Components/Details'
import Sidebar from './Components/Sidebar';

function App() {

  return (
    <>
    <Header />
      <div style={{marginTop:'155px'}}>
        <SortContextProvider>
        <SearchContextProvider>
      <Routes>
        <Route path="/" element={<MainIndex />} />
        <Route path="/:key" element={<DetailsContainer />} />
      </Routes>
      </SearchContextProvider>
      </SortContextProvider>
      </div>
    <Footer />
    </>
  );
}

function Header() {
  return (
      <header>
        <div style={{paddingLeft:'20px'}}>
        <h1>
          <a href="http://aiidateam.github.io/aiida-registry"><img src={whiteLogo} height="70px" /></a>
        </h1>
        <p style={{ fontSize: '90%' }}>
          <a href="http://github.com/aiidateam/aiida-registry" style={{ color: '#999' }}>[View on GitHub/register your package]</a>
        </p>
        </div>
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
 * @returns {JSX.Element} JSX element representing the DetailsContainer.
 */

function DetailsContainer() {
  const { key } = useParams();
  useEffect(() => {
    //Decrease the footer width on the details page to save some space for the sidebar.
    document.querySelector('footer').style.width = 'calc(100% - 380px)';

    // Clean up the styling when the component unmounts
    return () => {
      document.querySelector('footer').style.width = 'calc(100% - 64px)'; // Revert to default styles
    };
  }, []);
  function setupScrollBehavior() {
    //Display the header and move the sidebar under it when scrolling up
    //& Hide the header and align sidebar to top when scrolling down.
    var prevScrollpos = window.scrollY;
    window.onscroll = function() {
    var currentScrollPos = window.scrollY;
      if (prevScrollpos > currentScrollPos) {
        document.querySelector("header").style.top = "0";
        document.querySelector("#sidebar .MuiDrawer-paper").style.marginTop = '155px';
      } else {
        if (prevScrollpos > 150) {
        document.querySelector("header").style.top = "-155px";
        document.querySelector("#sidebar .MuiDrawer-paper").style.marginTop = '0';
        }
      }
      prevScrollpos = currentScrollPos;
    }
    }
    setupScrollBehavior();

  return (
      <>
      <div id='detailsContainer'>
          <Details pluginKey={key} />
          <Sidebar pluginKey={key} />
          </div>
      </>
  );
}

export default App;
