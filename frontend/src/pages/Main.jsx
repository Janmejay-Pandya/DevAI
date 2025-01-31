import Chat from "../components/Main/Chat";
import Preview from "../components/Main/Preview";
import Terminal from "../components/Main/Terminal";

const Main = () => {
  return (
    <div className="flex h-[calc(100vh-58px)]">
      <div className="w-1/2">
        <Chat />
      </div>

      <div className="w-1/2 flex flex-col">
        <div className="h-1/2">
          <Preview />
        </div>
        <div className="h-1/2">
          <Terminal />
        </div>
      </div>
    </div>
  );
};

export default Main;
