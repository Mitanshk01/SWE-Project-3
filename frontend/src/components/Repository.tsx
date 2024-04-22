const Repository = ({ repository }) => {
    return (
      <div>
        <h2>{repository.name}</h2>
        {/* <p>{repository.description}</p> */}
        {/* Render other repository details here */}
      </div>
    );
  };
  
  export default Repository;