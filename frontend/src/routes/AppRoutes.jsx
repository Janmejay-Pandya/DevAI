import { Route, Routes } from "react-router-dom";
import Navbar from "../components/commons/Navbar";
import Main from "../pages/Main";
import Login from "../components/Login/Login";
import Register from "../components/Register/Register";
import ThemePicker from "../components/Themepicker/ThemePicker";
import PreviewPage from "../components/PreviewPage/PreviewPage";
import NewProject from "../pages/NewProject";
import ProtectedRoute from "./ProtectedRoutes";

const AppRoutes = () => {
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/login/" element={<Login />} />
        <Route path="/register/" element={<Register />} />
        <Route path="/themepicker/" element={<ThemePicker />} />
        <Route path="/previewpage/" element={<PreviewPage />} />
        <Route
          path="/new-project"
          element={
            <ProtectedRoute>
              <NewProject />
            </ProtectedRoute>
          }
        />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Main />
            </ProtectedRoute>
          }
        />
      </Routes>
    </>
  );
};

export default AppRoutes;
