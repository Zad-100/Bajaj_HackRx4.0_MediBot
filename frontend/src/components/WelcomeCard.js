import logo from '../assets/medibot-logo.png'

function WelcomeCard() {
  return (
    <div className='flex flex-col gap-2 my-5 mx-4 justify-center items-center'>
      <img src={logo} className=' w-28'/>
      <div>
      <div className='flex gap-2 text-2xl font-bold'>
        <h1>Welcome to</h1>
        <h1 className='text-[#7F79F1]'>Medibot</h1>
      </div>
      <p className='text-sm'>Medical questions? I got you covered!</p>
      </div>
    </div>
  )
}

export default WelcomeCard
