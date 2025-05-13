import React, { useEffect, useState } from 'react';

const FlashSalesTimer = ({ deadline }) => {
  const calculateTimeLeft = () => {
    const difference = +new Date(deadline) - +new Date();
    let timeLeft = {};
    if (difference > 0) {
      timeLeft = {
        days: Math.floor(difference / (1000 * 60 * 60 * 24)),
        hours: Math.floor((difference / (1000 * 60 * 60)) % 24),
        minutes: Math.floor((difference / 1000 / 60) % 60),
        seconds: Math.floor((difference / 1000) % 60),
      };
    }
    return timeLeft;
  };

  const [timeLeft, setTimeLeft] = useState(calculateTimeLeft());
  
  useEffect(() => {
    const timer = setInterval(() => setTimeLeft(calculateTimeLeft()), 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="flex items-center gap-1">
      <div className="flex flex-col items-center">
        <div className="text-lg font-bold">{String(timeLeft.days || 0).padStart(2, '0')}</div>
        <div className="text-xs">Days</div>
      </div>
      <span className="text-lg font-bold mx-1">:</span>
      <div className="flex flex-col items-center">
        <div className="text-lg font-bold">{String(timeLeft.hours || 0).padStart(2, '0')}</div>
        <div className="text-xs">Hours</div>
      </div>
      <span className="text-lg font-bold mx-1">:</span>
      <div className="flex flex-col items-center">
        <div className="text-lg font-bold">{String(timeLeft.minutes || 0).padStart(2, '0')}</div>
        <div className="text-xs">Minutes</div>
      </div>
      <span className="text-lg font-bold mx-1">:</span>
      <div className="flex flex-col items-center">
        <div className="text-lg font-bold">{String(timeLeft.seconds || 0).padStart(2, '0')}</div>
        <div className="text-xs">Seconds</div>
      </div>
    </div>
  );
};

export default FlashSalesTimer;