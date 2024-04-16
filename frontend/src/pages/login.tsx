import React from 'react';
import AuthForm from '../components/AuthForm';

const LoginPage = () => {
  return (
    <div>
      <h1 className="text-center text-2xl font-bold my-4">Login</h1>
      <AuthForm mode="login" />
    </div>
  );
};

export default LoginPage;