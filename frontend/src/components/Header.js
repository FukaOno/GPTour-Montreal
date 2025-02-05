import React from "react";
import { Link, useLocation } from "react-router-dom"; // Import useLocation
import { useLanguage } from "../App";
import DiscoverMontreal from "./DiscoverMontreal";

function Header() {
  const { language } = useLanguage();
  const location = useLocation(); // Get the current location

  const translations = {
    en: {
      header: "Montréal Explorer",
      aboutMontreal: "Discover the City",
      aboutUs: "About Us",
    },
    fr: {
      header: "Montréal Explorer",
      aboutMontreal: "Découvrez la ville",
      aboutUs: "Notre Équipe",
    },
  };

  return (
    <header className="headerSection">
      <div className="header">
        {/* Montreal Explorer linked to the homepage */}
        <Link to="/" style={{ textDecoration: "none", color: "black" }}>
          {translations[language].header.split(" ")[0]}{" "}
          <span style={{ fontSize: "50px" }}>
            {translations[language].header.split(" ")[1]}
          </span>
        </Link>
      </div>
      <nav>
        <ul className="nav-list">
          {/* Show "ABOUT MONTREAL" and "ABOUT US" only on the homepage */}
          {location.pathname === "/" && (
            <>
              <li>
                <Link to="./DiscoverMontreal">{translations[language].aboutMontreal}</Link>
              </li>
              <li>
              <Link to="./AboutUs">{translations[language].aboutUs}</Link>
              </li>
            </>
          )}
        </ul>
      </nav>
    </header>
  );
}

export default Header;