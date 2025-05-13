import React, { useState, useEffect } from 'react';
import { FaTwitter, FaInstagram, FaLinkedinIn } from 'react-icons/fa';

const About = () => {
  const [activeStatIndex, setActiveStatIndex] = useState(null);
  const [currentTeamSlide, setCurrentTeamSlide] = useState(0);

  const teamMembers = [
    { name: "Will Smith", role: "Founder & Chairman", image: "/Will-Smith.jpg", social: { twitter: "#", instagram: "#", linkedin: "#" } },
    { name: "Emma Watson", role: "Managing Director", image: "/Emma-Watson.jpg", social: { twitter: "#", instagram: "#", linkedin: "#" } },
    { name: "Tom Cruise", role: "Product Designer", image: "/Tom-Cruise.jpg", social: { twitter: "#", instagram: "#", linkedin: "#" } },
    { name: "Sarah Johnson", role: "Head of Marketing", image: "/Sarah-Johnson.webp", social: { twitter: "#", instagram: "#", linkedin: "#" } },
    { name: "David Chen", role: "Lead Developer", image: "/David-Chen.jpg", social: { twitter: "#", instagram: "#", linkedin: "#" } },
    { name: "Maria Garcia", role: "UX Designer", image: "/Maria-Garcia.jpg", social: { twitter: "#", instagram: "#", linkedin: "#" } },
    { name: "James Wilson", role: "Operations Manager", image: "/James-Wilson.jpg", social: { twitter: "#", instagram: "#", linkedin: "#" } },
    { name: "Lisa Anderson", role: "Customer Success Manager", image: "/Lisa-Anderson.jpg", social: { twitter: "#", instagram: "#", linkedin: "#" } },
    { name: "Cecil Leon", role: "QA Engineer", image: "/Cecil-Leon.jpg", social: { twitter: "#", instagram: "#", linkedin: "#" } },
  ];

  const stats = [
    { number: "10.5k", title: "Sellers active our site", icon: "store" },
    { number: "33k", title: "Monthly Product Sale", icon: "dollar" },
    { number: "95.5k", title: "Customer active in our site", icon: "users" },
    { number: "25M", title: "Anual gross sale in our site", icon: "money" }
  ];

  const totalTeamPages = Math.ceil(teamMembers.length / 3);

  // Auto-rotate team slides
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTeamSlide(prev => (prev === totalTeamPages - 1 ? 0 : prev + 1));
    }, 5000);
    return () => clearInterval(interval);
  }, [totalTeamPages]);

  // Render team members for current page
  const renderTeamMembers = () => {
    const startIndex = currentTeamSlide * 3;
    const endIndex = Math.min(startIndex + 3, teamMembers.length);
    const currentPageMembers = teamMembers.slice(startIndex, endIndex);

    return (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {currentPageMembers.map((member, index) => (
          <div key={index} className="bg-white rounded-lg shadow-md hover:shadow-lg">
            <img 
              src={member.image} 
              alt={member.name} 
              className="w-full aspect-square object-cover mb-4 rounded-lg shadow-sm"
            />
            <h3 className="text-xl pl-4 font-bold">{member.name}</h3>
            <p className="text-gray-600 pl-4 mb-4">{member.role}</p>
            <div className="flex pl-4 pb-4 gap-2">
              <a href={member.social.twitter} className="text-gray-600 hover:text-black">
                <FaTwitter size={18} />
              </a>
              <a href={member.social.instagram} className="text-gray-600 hover:text-black">
                <FaInstagram size={18} />
              </a>
              <a href={member.social.linkedin} className="text-gray-600 hover:text-black">
                <FaLinkedinIn size={18} />
              </a>
            </div>
          </div>
        ))}
      </div>
    );
  };

  // Render the icon based on stat type
  const renderStatIcon = (iconType, isHighlighted) => {
    const iconColor = isHighlighted ? "white" : "black";
    const bgColor = isHighlighted ? "bg-red-400" : "bg-gray-200";
    
    switch(iconType) {
      case 'store':
        return (
          <div className={`${bgColor} rounded-full p-4 flex items-center justify-center`}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M20 7H4C2.9 7 2 7.9 2 9V15C2 16.1 2.9 17 4 17H5V19C5 20.1 5.9 21 7 21H17C18.1 21 19 20.1 19 19V17H20C21.1 17 22 16.1 22 15V9C22 7.9 21.1 7 20 7Z" stroke={iconColor} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M6 7V5C6 4.46957 6.21071 3.96086 6.58579 3.58579C6.96086 3.21071 7.46957 3 8 3H16C16.5304 3 17.0391 3.21071 17.4142 3.58579C17.7893 3.96086 18 4.46957 18 5V7" stroke={iconColor} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
        );
      case 'dollar':
        return (
          <div className={`${bgColor} rounded-full p-4 flex items-center justify-center`}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="10" stroke={iconColor} strokeWidth="2"/>
              <path d="M12 6V18" stroke={iconColor} strokeWidth="2" strokeLinecap="round"/>
              <path d="M15 9.5C15 8.12 13.88 7 12.5 7H11.5C10.12 7 9 8.12 9 9.5C9 10.88 10.12 12 11.5 12H12.5C13.88 12 15 13.12 15 14.5C15 15.88 13.88 17 12.5 17H11.5C10.12 17 9 15.88 9 14.5" stroke={iconColor} strokeWidth="2" strokeLinecap="round"/>
            </svg>
          </div>
        );
      case 'users':
        return (
          <div className={`${bgColor} rounded-full p-4 flex items-center justify-center`}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M17 21V19C17 17.9391 16.5786 16.9217 15.8284 16.1716C15.0783 15.4214 14.0609 15 13 15H5C3.93913 15 2.92172 15.4214 2.17157 16.1716C1.42143 16.9217 1 17.9391 1 19V21" stroke={iconColor} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M9 11C11.2091 11 13 9.20914 13 7C13 4.79086 11.2091 3 9 3C6.79086 3 5 4.79086 5 7C5 9.20914 6.79086 11 9 11Z" stroke={iconColor} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M23 21V19C22.9993 18.1137 22.7044 17.2528 22.1614 16.5523C21.6184 15.8519 20.8581 15.3516 20 15.13" stroke={iconColor} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M16 3.13C16.8604 3.35031 17.623 3.85071 18.1676 4.55232C18.7122 5.25392 19.0078 6.11683 19.0078 7.005C19.0078 7.89318 18.7122 8.75608 18.1676 9.45769C17.623 10.1593 16.8604 10.6597 16 10.88" stroke={iconColor} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
        );
      case 'money':
        return (
          <div className={`${bgColor} rounded-full p-4 flex items-center justify-center`}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" stroke={iconColor} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M16 8H13.5C12.5717 8 11.6815 8.36875 11.0251 9.02513C10.3687 9.6815 10 10.5717 10 11.5C10 12.4283 10.3687 13.3185 11.0251 13.9749C11.6815 14.6313 12.5717 15 13.5 15H14.5C15.4283 15 16.3185 15.3687 16.9749 16.0251C17.6313 16.6815 18 17.5717 18 18.5C18 19.4283 17.6313 20.3185 16.9749 20.9749C16.3185 21.6313 15.4283 22 14.5 22H8" stroke={iconColor} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M12 0V24" stroke={iconColor} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="w-full">
      {/* Breadcrumb */}
      <div className="py-4 px-8">
        <div className="flex items-center text-sm">
          <a href="/" className="text-gray-500 hover:text-black">Home</a>
          <span className="mx-2 text-gray-500">/</span>
          <span className="font-medium">About</span>
        </div>
      </div>

      {/* Our Story */}
      <div className="flex flex-col md:flex-row px-8 py-12 gap-8">
        <div className="md:w-1/2">
          <h1 className="text-4xl font-bold mb-6">Our Story</h1>
          <p className="mb-4">
          Founded in 2024, ShopMeeting has quickly become Kenya’s leading online shopping marketplace, with a strong nationwide presence. Backed by a wide range of tailored marketing, data and service solutions, ShopMeeting connects over 10,500 sellers and 300 brands with more than 3 million customers across the country.
          </p>
          <p>
          With a fast-growing catalog of over 1 million products, ShopMeeting offers a diverse assortment across categories — from everyday consumer goods to specialty items — all aimed at delivering convenience, variety and value to our users.
          </p>
        </div>
        <div className="md:w-1/2">
          <img src="/woman-shopping.jpg" alt="Woman shopping" className="w-full rounded-lg" />
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 px-8 py-12">
        {stats.map((stat, index) => (
          <div
            key={index}
            className={`border rounded-lg p-6 flex flex-col items-center justify-center cursor-pointer transition-all duration-300
              ${activeStatIndex === index ? 'bg-red-500 text-white transform scale-105 shadow-lg' : 'bg-white hover:shadow-md'}`}
            onClick={() => setActiveStatIndex(index)}
          >
            {renderStatIcon(stat.icon, activeStatIndex === index)}
            <div className={`text-3xl font-bold mt-4 transition-all duration-300 ${activeStatIndex === index ? 'transform scale-110' : ''}`}>
              {stat.number}
            </div>
            <div className="text-sm text-center mt-2">{stat.title}</div>
          </div>
        ))}
      </div>

      {/* Team Section */}
      <div className="bg-gray-50 px-8 py-12">
        {renderTeamMembers()}
        
        {/* Pagination dots */}
        <div className="flex justify-center mt-8">
          {Array.from({ length: totalTeamPages }).map((_, index) => (
            <button
              key={index}
              onClick={() => setCurrentTeamSlide(index)}
              className={`w-2 h-2 mx-1 rounded-full ${
                index === currentTeamSlide ? 'bg-black' : 'bg-gray-300'
              }`}
              aria-label={`Go to team page ${index + 1}`}
            />
          ))}
        </div>
      </div>

      {/* Services */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 px-8 py-12">
        {[
          {
            icon: (
              <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 2L2 7L12 12L22 7L12 2Z" />
                <path d="M2 17L12 22L22 17" />
                <path d="M2 12L12 17L22 12" />
              </svg>
            ),
            title: "FREE AND FAST DELIVERY",
            desc: "Free delivery for all orders over $150"
          },
          {
            icon: (
              <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10" />
                <path d="M8 14s1.5 2 4 2 4-2 4-2" />
                <line x1="9" y1="9" x2="9.01" y2="9" />
                <line x1="15" y1="9" x2="15.01" y2="9" />
              </svg>
            ),
            title: "24/7 CUSTOMER SERVICE",
            desc: "Friendly 24/7 customer support"
          },
          {
            icon: (
              <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
              </svg>
            ),
            title: "MONEY BACK GUARANTEE",
            desc: "We return money within 30 days"
          }
        ].map((service, idx) => (
          <div key={idx} className="flex flex-col items-center text-center">
            <div className="bg-gray-100 rounded-full p-6 mb-4 flex items-center justify-center">
              {service.icon}
            </div>
            <h3 className="text-lg font-bold uppercase mb-2">{service.title}</h3>
            <p className="text-gray-600">{service.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default About;