import React, { useEffect, useState } from 'react';
import { io } from 'socket.io-client';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPhoneAlt, faEnvelope } from '@fortawesome/free-solid-svg-icons';
import { Link } from 'react-router-dom';
import API_URL from '../utils/apiConfig';

const socket = io(API_URL, {
  transports: ['websocket', 'polling'],
  withCredentials: true,
  auth: {
    token: localStorage.getItem('token')
  }
});

const Contact = () => {
  const [form, setForm] = useState({ name: '', email: '', subject: '', message: '' });
  const [status, setStatus] = useState('');
  const [chatInput, setChatInput] = useState('');
  const [chatMessages, setChatMessages] = useState([]);
  const currentUser = { id: 'Timothy' }; // Replace with actual user ID
  const ticketId = 'ticket456'; // Replace with actual ticket ID

  useEffect(() => {
    socket.on('contact_form_status', (res) => {
      if (res.success) {
        setStatus('Message sent successfully!');
        setForm({ name: '', email: '', subject: '', message: '' });
      } else {
        setStatus(`Failed to send: ${res.error}`);
      }
    });

    socket.emit('join_chat', {
      user_id: currentUser.id,
      ticket_id: ticketId
    });

    socket.on('new_message', (message) => {
      setChatMessages((prev) => [...prev, message]);
    });

    return () => {
      socket.emit('leave_chat', { ticket_id: ticketId });
      socket.off('new_message');
      socket.off('contact_form_status');
    };
  }, [currentUser.id, ticketId]);

  const handleSubmit = (e) => {
    e.preventDefault();
    socket.emit('contact_form', form);
    setStatus('Sending...');
  };

  const handleChange = (e) => setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));

  const sendMessage = () => {
    if (chatInput.trim() === '') return;
    socket.emit('chat_message', {
      user_id: currentUser.id,
      ticket_id: ticketId,
      message: chatInput
    });
    setChatInput('');
  };

  return (
    <div className="bg-white text-gray-900 py-6 px-4 sm:px-6 lg:px-8">
      <div className="flex flex-col md:flex-row md:space-x-8 max-w-7xl mx-auto">
        {/* Left Contact Info */}
        <section className="bg-white border border-gray-100 rounded-md shadow-sm p-6 mb-4 md:mb-0 md:w-1/3 space-y-8">
          <div className="flex items-start space-x-4">
            <div className="bg-black rounded-full p-3 text-white shrink-0">
              <FontAwesomeIcon icon={faPhoneAlt} className="text-base" />
            </div>
            <div className="text-sm text-gray-900">
              <p className="font-semibold mb-1">Call Us</p>
              <p className="mb-1">We are available <b>24/7</b>, 7 days a week.</p>
              <p className="border-t border-gray-300 pt-1">Phone: <b>+254722222256</b></p>
            </div>
          </div>
          <div className="flex items-start space-x-4">
            <div className="bg-black rounded-full p-3 text-white shrink-0">
              <FontAwesomeIcon icon={faEnvelope} className="text-base" />
            </div>
            <div className="text-sm text-gray-900">
              <p className="font-semibold mb-1">Email Us</p>
              <p className="mb-1">Fill out our form and we will contact you within 24 hours.</p>
              <p>Emails: <b>customer@ShopMeet.com</b></p>
              <p>Emails: <b>customer@ShopMeet.com</b></p>
            </div>
          </div>
        </section>

        {/* Right Contact Form */}
        <section className="bg-white border border-gray-100 rounded-md shadow-sm p-6 md:w-2/3">
          <form className="space-y-4" onSubmit={handleSubmit}>
            <div className="flex flex-col sm:flex-row sm:space-x-4 space-y-4 sm:space-y-0">
              <input
                type="text"
                name="name"
                value={form.name}
                onChange={handleChange}
                placeholder="Your Name *"
                required
                className="flex-1 bg-gray-100 border border-gray-200 rounded px-3 py-3 text-sm placeholder:text-gray-400 focus:outline-none focus:ring-1 focus:ring-black focus:border-black"
              />
              <input
                type="email"
                name="email"
                value={form.email}
                onChange={handleChange}
                placeholder="Your Email *"
                required
                className="flex-1 bg-gray-100 border border-gray-200 rounded px-3 py-3 text-sm placeholder:text-gray-400 focus:outline-none focus:ring-1 focus:ring-black focus:border-black"
              />
              <input
                type="tel"
                name="phone"
                value={form.phone}
                onChange={handleChange}
                placeholder="Your Phone *"
                required
                className="flex-1 bg-gray-100 border border-gray-200 rounded px-3 py-3 text-sm placeholder:text-gray-400 focus:outline-none focus:ring-1 focus:ring-black focus:border-black"
              />
            </div>
            <textarea
              rows="5"
              name="message"
              value={form.message}
              onChange={handleChange}
              placeholder="Your Message"
              className="w-full bg-gray-100 border border-gray-200 rounded px-3 py-3 text-sm placeholder:text-gray-400 resize-none focus:outline-none focus:ring-1 focus:ring-black focus:border-black"
            ></textarea>
            <div className="flex justify-end">
              <button
                type="submit"
                className="bg-black text-white text-sm font-semibold rounded px-6 py-2 hover:bg-gray-800 transition"
              >
                Send Feedback
              </button>
            </div>
            {status && <p className="text-sm text-green-600">{status}</p>}
          </form>
        </section>
      </div>

      {/* Live Chat Section */}
      <div className="max-w-4xl mx-auto mt-10 border border-gray-200 rounded-lg p-4">
        <h2 className="text-lg font-semibold mb-2">Chat</h2>
        <div className="h-48 overflow-y-auto border rounded-md p-2 mb-2 bg-gray-50">
          {chatMessages.map((msg, idx) => (
            <div key={idx} className="text-sm mb-1">
              <span className="font-semibold text-gray-700">{msg.user_id}:</span> {msg.message}
            </div>
          ))}
        </div>
        <div className="flex space-x-2">
          <input
            type="text"
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            placeholder="Type your message..."
            className="flex-1 border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none"
          />
          <button
            onClick={sendMessage}
            className="bg-black text-white px-4 py-2 rounded text-sm hover:bg-gray-800"
          >
            Send
          </button>
        </div>
      </div>

      {/* Link to FAQ Page */}
      <div className="mt-6 text-center">
        <Link
          to="/faq"
          className="text-sm text-black font-semibold hover:underline hover:text-gray-700"
        >
          Still need help? Check our FAQs →
        </Link>
      </div>
    </div>
  );
};

export default Contact;
