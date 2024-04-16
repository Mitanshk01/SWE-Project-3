import Link from 'next/link';

const HomePage = () => {
  return (
    <div className="text-center">
      <h1 className="text-4xl font-bold my-4">Welcome to Our Site!</h1>
      <Link href="/login" className="text-indigo-600 hover:text-indigo-800">
        Login
      </Link>
      {' | '}
      <Link href="/register" className="text-indigo-600 hover:text-indigo-800">
        Register
      </Link>
    </div>
  );
};

export default HomePage;