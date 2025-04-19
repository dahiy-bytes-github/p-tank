import React from "react";
import "../styles/Logo.css"; 
const Logo = () => {
  const imageUrl ="https://res.cloudinary.com/uf-552861/image/upload/v1722409863/printed_circuit_board_layout_vgmgll.jpg";
  return (
    <div className="logo-container">
      <img src={imageUrl} alt="PCB" className="logo" />
    </div>
  );
};

export default Logo;
