import React from "react";
import './OfflineData.css';
import FlickerBox from './FlickerBox';

function OfflineData() {
  const characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
  return (
    <div className="OfflineData">
      
      {
        [...characters].map((el, index) => 
          <FlickerBox 
          text={el}
          freq={index+10}
          ops={true}
          key={index}
          />
        )
      }
    </div>
  );
}

export default OfflineData;
