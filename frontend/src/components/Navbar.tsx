import React from 'react';
import Link from 'next/link';

const Navbar = () => {
  return (
    <nav className="flex justify-end py-4 px-8 bg-gray-800">
      <ul className="flex space-x-4">
        <li>
          <Link href="/login">
            <div className="text-white hover:text-gray-300 cursor-pointer bg-indigo-600 px-4 py-2 rounded-lg transition duration-300 ease-in-out hover:bg-indigo-700">
              Login
            </div>
          </Link>
        </li>
        <li>
          <Link href="/register">
            <div className="text-white hover:text-gray-300 cursor-pointer bg-indigo-600 px-4 py-2 rounded-lg transition duration-300 ease-in-out hover:bg-indigo-700">
              Register
            </div>
          </Link>
        </li>
      </ul>
    </nav>
  );
};

export default Navbar;
