import { Route, Routes } from "react-router-dom";
import Navbar from "../components/commons/Navbar";
import Main from "../pages/Main";

const AppRoutes = () => {
  return (
    <>
      <Navbar />
      <Routes>
        <Route index path="/" element={<Main />} />
      </Routes>
    </>
  );
};

export default AppRoutes;
