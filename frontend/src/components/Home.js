import { useState } from "react"
import { HiMenu } from "react-icons/hi"
import Feed from "./Feed"
import ChatBox from "./ChatBox"
import Sidebar from "./Sidebar"

function Home() {
  const [messages,setMessages]=useState([]);//array of objects
  const [currentMessage,setCurrentMessage]=useState({}); //object for sources and userText
  const [toggleSidebar, setToggleSidebar] = useState(false);
  const [sources,setSources]=useState([]);
  const [currentReply,setCurrentReply]=useState({}) //object for sources and replies returning 
  const [reply,setReply]=useState([]); //array of objects for replies

  return (
    <div className="flex md:flex-row-reverse flex-col  bg-[#EEF1F8] h-screen">
      <div className=" hidden md:flex h-screen">
        <Sidebar setSources={setSources}/>
      </div>
      <div className="flex md:hidden flex-row">
        <div className="flex flex-row justify-between ml-8 w-screen p-6 text-xl font-semibold ">
          <div>
            <HiMenu
              fontSize={40}
              className="cursor-pointer"
              onClick={() => setToggleSidebar(true)}
            />
          </div>
        </div>
        {toggleSidebar && (
          <div className="fixed bg-white h-screen shadow-md z-10">
            <Sidebar setToggleSidebar={setToggleSidebar} setSources={setSources}/>
          </div>
        )}
      </div>
      <div className=" flex h-full overflow-y-scroll items-center  flex-col justify-between ">
        <div className="w-full overflow-x-hidden ">
        <Feed messages={messages} reply={reply}/>
        </div>
          <div className="w-full bottom-0 mb-3 mt-3">
            <ChatBox setCurrentMessage={setCurrentMessage} sources={sources} messages={messages} setMessages={setMessages} currentMessage={currentMessage} currentReply={currentReply} setCurrentReply={setCurrentReply} setReply={setReply} reply={reply}/>
          </div>
      </div>

    </div>
  );
}

export default Home;
