import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faArrowLeft } from '@fortawesome/free-solid-svg-icons';

const faqs = [
  {
    question: 'How do I contact customer support?',
    answer: 'You can contact customer support through our contact page where you can send a message and receive replies via chat.',
  },
  {
    question: 'How long does it take to get a response?',
    answer: 'We typically respond within 24–48 hours during business days.',
  },
  {
    question: 'Can I track previous support requests?',
    answer: 'Yes, once logged in, you can view previous support threads in your profile section.',
  },
  {
    question: 'What if I forgot my login credentials?',
    answer: 'Click "Forgot password" on the login page and follow the instructions sent to your email.',
  },
];

const FaqPage = () => {
  const [activeIndex, setActiveIndex] = useState(null);

  const toggleFaq = (index) => {
    setActiveIndex(activeIndex === index ? null : index);
  };

  return (
    <div className="relative max-w-3xl mx-auto px-4 py-12">
      <Link
        to="/contact"
        className="absolute top-4 left-4 bg-red-600 text-white p-2 rounded-full hover:bg-red-700 transition"
      >
        <FontAwesomeIcon icon={faArrowLeft} />
      </Link>

      <h1 className="text-3xl font-bold mb-6 text-center text-gray-800">Frequently Asked Questions</h1>
      <div className="space-y-4">
        {faqs.map((faq, index) => (
          <div key={index} className="border rounded-xl p-4 bg-white shadow-sm">
            <button
              onClick={() => toggleFaq(index)}
              className="flex justify-between w-full text-left text-lg font-medium text-gray-900"
            >
              {faq.question}
              <span className="ml-4">{activeIndex === index ? '-' : '+'}</span>
            </button>
            {activeIndex === index && (
              <p className="mt-3 text-gray-600 text-base">{faq.answer}</p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default FaqPage;
