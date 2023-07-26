import { useState ,useEffect} from 'react';
import searchs from '../assets/Search-alt.svg'

const items=["CDC","NHS","WebSite2","WebMD","WebSite-3","WebSite4"]

function FilterOption({ setSources }) {

    const [selectedFilters, setSelectedFilters] = useState([]);

    const handleFilterButtonClick = (selectedCategory) => {
        if (selectedFilters.includes(selectedCategory)) {
          let filters = selectedFilters.filter((el) => el !== selectedCategory);
          setSelectedFilters(filters);
        } else {
          setSelectedFilters([...selectedFilters, selectedCategory]);
        }
      };

      useEffect(() => {
        setSources(selectedFilters);
      }, [selectedFilters]);

  return (
    <div className='bg-sky-200  flex justify-center items-center w-full h-full flex-col px-6 gap-8'>
        <div className="text-black flex items-center flex-col bg-search gap-2 mx-2">
            <div className=' flex border-sky-200 border-b-black border-2'>
                <input type='search' className='font-bold bg-sky-200 placeholder-black text-xl border-transparent focus:outline-0 ' placeholder='Tailor your search '/>
                <img src={searchs} />
            </div>
            <p className='text-sm font-serif '>Choose from the available websites/databases according to your preferences and get medical answers as desired! </p>
        </div>
        
        <div className='grid grid-cols-3 gap-x-2 gap-y-3 container px-10'>
            {items.map((opt,idx)=>(
                <button 
                  onClick={() => handleFilterButtonClick(opt)}
                  className={`px-2  text-sm text-center rounded-full   font-semibold ${
                    selectedFilters?.includes(opt) ? "bg-[#7F79F1] text-white" : "bg-white"
                  }`  }
                  key={`filters-${idx}`}>
                        {opt}
                </button>
            ))}
        </div>
    </div>
  )
}

export default FilterOption

