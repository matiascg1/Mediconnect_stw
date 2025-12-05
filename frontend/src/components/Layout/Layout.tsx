import type React from "react"
import Header from "./Header"

interface LayoutProps {
  children: React.ReactNode
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-secondary-50 flex flex-col">
      <Header />
      <main className="flex-grow container-custom py-8 animate-in fade-in duration-500">
        {children}
      </main>
      <footer className="bg-white border-t border-secondary-200 mt-auto">
        <div className="container-custom py-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <p className="text-secondary-500 text-sm">
              © {new Date().getFullYear()} MediConnect. All rights reserved.
            </p>
            <div className="flex space-x-6 mt-4 md:mt-0">
              <a href="#" className="text-secondary-400 hover:text-primary-600 text-sm">Privacy Policy</a>
              <a href="#" className="text-secondary-400 hover:text-primary-600 text-sm">Terms of Service</a>
              <a href="#" className="text-secondary-400 hover:text-primary-600 text-sm">Contact Support</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default Layout