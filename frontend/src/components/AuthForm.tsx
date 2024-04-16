// import React, { useState } from 'react';
// import axios from 'axios';

// const AuthForm = ({ mode }) => {
//   const [username, setUsername] = useState('');
//   const [password, setPassword] = useState('');
//   const [error, setError] = useState('');

//   const handleSubmit = async (e) => {
//     e.preventDefault();
//     setError('');

//     const url = mode === 'login' ? '/auth/login' : '/auth/register';
//     try {
//       console.log("Sending request")
//       console.log("username", username)
//       console.log("password", password)
//       console.log("url", url) 
//       const response = await axios.post(url, { username, password });
//       console.log('response', response.data);
//       // Redirect or save token in local storage or context
//     } catch (err) {
//       console.error(err);
//       setError(err.response?.data.error || 'Something went wrong');
//     }
//   };

//   return (
//     <div className="max-w-sm mx-auto my-10 p-5 border rounded shadow">
//       <form onSubmit={handleSubmit} className="space-y-5">
//         <div>
//           <label htmlFor="username" className="block text-sm font-medium text-gray-700">
//             Username
//           </label>
//           <input
//             type="text"
//             id="username"
//             value={username}
//             onChange={(e) => setUsername(e.target.value)}
//             className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
//             required
//           />
//         </div>
//         <div>
//           <label htmlFor="password" className="block text-sm font-medium text-gray-700">
//             Password
//           </label>
//           <input
//             type="password"
//             id="password"
//             value={password}
//             onChange={(e) => setPassword(e.target.value)}
//             className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
//             required
//           />
//         </div>
//         {error && <p className="text-red-500 text-xs italic">{error}</p>}
//         <button type="submit" className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
//           {mode === 'login' ? 'Log In' : 'Register'}
//         </button>
//       </form>
//     </div>
//   );
// };

// export default AuthForm;


import React, { useState } from 'react';
import axios from 'axios';

const AuthForm = ({ mode }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    // Setting the API endpoint based on the mode (login or register)
    const url = `http://localhost:4003/auth/${mode}`;
    console.log("Sending request")
    console.log("username", username)
    console.log("password", password)

    try {
      console.log("Trying to send request")
      // Send a POST request to the server with username and password
      const response = await axios.post(url, { username, password });
      console.log('Response:', response.data);
      if (mode === 'register') {
        // If registration is successful, clear the form and show a success message
        setSuccess('Registration successful! You can now login.');
        setUsername('');
        setPassword('');
      } else {
        setSuccess('Login successful!');
        console.log('Token:', response.data.token);  // Log the token or save it in localStorage
      }
    } catch (err) {
      // Display error message if the API call fails
      setError(err.response?.data.error || 'Something went wrong');
    }
  };

  return (
    <div className="max-w-md mx-auto my-10 bg-white p-8 border rounded-lg shadow-strong">
      <h2 className="text-center text-2xl font-bold text-dark-blue mb-6">{mode === 'login' ? 'Login' : 'Register'}</h2>
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label htmlFor="username" className="block text-sm font-medium text-gray-700">Username</label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="mt-1 block w-full px-4 py-2 bg-light-blue border border-gray-300 rounded-md shadow-sm focus:ring-brand-blue focus:border-brand-blue"
            required
          />
        </div>
        <div>
          <label htmlFor="password" className="block text-sm font-medium text-gray-700">Password</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1 block w-full px-4 py-2 bg-light-blue border border-gray-300 rounded-md shadow-sm focus:ring-brand-blue focus:border-brand-blue"
            required
          />
        </div>
        {error && <p className="text-red-500 text-xs italic">{error}</p>}
        {success && <p className="text-green-500 text-xs italic">{success}</p>}
        <button type="submit" className="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-dark-blue hover:bg-brand-blue focus:outline-none">
          {mode === 'login' ? 'Log In' : 'Register'}
        </button>
      </form>
    </div>
  );
};

export default AuthForm;