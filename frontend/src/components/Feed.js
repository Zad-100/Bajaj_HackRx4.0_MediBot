import { useRef,useEffect } from 'react'

import WelcomeCard from './WelcomeCard'
import Info from './Info'
import Disclaimer from './Disclaimer'
import Message from './Message'

function Feed({messages,reply}) {
  const scrollRef = useRef();
  
  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className=' justify-center flex flex-col gap-4 mx-6 text-xs md:my-12 '>
      <WelcomeCard />
      <Info />
      <Disclaimer />
      <div className='flex flex-col gap-4 mt-8'>
        {messages.map((messenger,index)=>(
          <div className='flex flex-col gap-4' ref={scrollRef} key={`conversation-${index}`}>
            <Message userMessage={true} message={messenger.message} />
            <Message userMessage={false} sources={reply[index]["sources"]} message={reply[index]["reply"]} />
          </div>
        ))}
      </div>
    </div>
  )
}

export default Feed
