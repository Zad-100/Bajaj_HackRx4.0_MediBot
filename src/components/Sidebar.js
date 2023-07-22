import FilterOption from "./FilterOption";
import doctors from "../assets/Doctors-pana.svg"
import { AiFillCloseCircle } from "react-icons/ai";

const Sidebar = ({ setToggleSidebar, setSources }) => {

    return (
        <div 
          className="relative flex flex-col bg-sky-200 gap-10 justify-between h-screen overflow-hidden w-[25em]  max-[480px]:min-w-[15em] items-center"
        >
          <div className="absolute md:hidden w-full text-black flex justify-end items-center p-2">
              <AiFillCloseCircle
                fontSize={30}
                className="cursor-pointer"
                onClick={() => setToggleSidebar(false)}
              />
            </div>
            <div className="my-20 md:my-28">
              <FilterOption setSources={setSources}/>
            </div>
            <div className="absolute inset-x-0 bottom-0">
              <img src={doctors}/>
            </div>
        </div>
    )
}

export default Sidebar;