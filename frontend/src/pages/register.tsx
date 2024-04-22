import React from 'react';
import AuthForm from '../components/AuthForm';

const RegisterPage = () => {
  return (
    <div>
      <h1 className="text-center text-2xl font-bold my-4">Register</h1>
      <AuthForm mode="register" />
    </div>
  );
};

export default RegisterPage;