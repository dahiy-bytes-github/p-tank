import React from "react";
import "../styles/Logo.css"; 

const Logo = () => {
  const imageUrl = "/assets/a-flat-vector-logo-.jpeg";

  return (
    <div className="logo-container">
      <img src={imageUrl} alt="Predictive Septic Tank Monitoring Logo" className="logo" />
    </div>
  );
};

export default Logo;
