/**
 * Validates if the given string is a properly formatted email address.
 * @param {string} email - The email address to validate.
 * @returns {boolean} - Returns true if the email is valid, otherwise false.
 */
export const validateEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };
  
  // Get the API URL from the environment variables
//   export const apiUrl = process.env.REACT_APP_API_URL;
  
//   if (!apiUrl) {
//     console.error("API URL is not defined! Check your .env file.");
//   }
  