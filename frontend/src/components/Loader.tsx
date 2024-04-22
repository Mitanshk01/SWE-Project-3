import styled, { keyframes } from 'styled-components';

const spin = keyframes`
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
`;

const LoaderDiv = styled.div`
  display: inline-block;
  width: 25px;
  height: 25px;
  border: 3px solid #f3f3f3;
  border-radius: 50%;
  border-top: 3px solid #3498db;
  animation: ${spin} 2s linear infinite;
`;

export function Loader() {
  return <LoaderDiv />;
}