// Form validation utility functions

/**
 * Validates an email address
 * @param {string} email - The email to validate
 * @returns {boolean} - True if valid, false otherwise
 */
export const isValidEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Validates a password
 * @param {string} password - The password to validate
 * @returns {object} - Object containing validity and message
 */
export const validatePassword = (password) => {
  if (!password) {
    return { isValid: false, message: 'Password is required' };
  }
  
  if (password.length < 8) {
    return { isValid: false, message: 'Password must be at least 8 characters long' };
  }
  
  // Check for at least one number
  if (!/\d/.test(password)) {
    return { isValid: false, message: 'Password must contain at least one number' };
  }
  
  // Check for at least one uppercase letter
  if (!/[A-Z]/.test(password)) {
    return { isValid: false, message: 'Password must contain at least one uppercase letter' };
  }
  
  return { isValid: true, message: '' };
};

/**
 * Validates a phone number
 * @param {string} phone - The phone number to validate
 * @returns {boolean} - True if valid, false otherwise
 */
export const isValidPhone = (phone) => {
  // Basic phone number validation (allows different formats)
  const phoneRegex = /^[+]?[(]?[0-9]{3}[)]?[-\s.]?[0-9]{3}[-\s.]?[0-9]{4,6}$/;
  return phoneRegex.test(phone);
};

/**
 * Validates a username
 * @param {string} username - The username to validate
 * @returns {object} - Object containing validity and message
 */
export const validateUsername = (username) => {
  if (!username) {
    return { isValid: false, message: 'Username is required' };
  }
  
  if (username.length < 3) {
    return { isValid: false, message: 'Username must be at least 3 characters long' };
  }
  
  // Only allow alphanumeric characters and underscores
  if (!/^[a-zA-Z0-9_]+$/.test(username)) {
    return { isValid: false, message: 'Username can only contain letters, numbers, and underscores' };
  }
  
  return { isValid: true, message: '' };
};

/**
 * Validates a name field
 * @param {string} name - The name to validate
 * @returns {boolean} - True if valid, false otherwise
 */
export const isValidName = (name) => {
  return name && name.trim().length > 0;
};

/**
 * Validates an address
 * @param {string} address - The address to validate
 * @returns {boolean} - True if valid, false otherwise
 */
export const isValidAddress = (address) => {
  return address && address.trim().length > 5;
};
