import React from 'react'
import { useTranslation } from 'react-i18next'
import { NavLink, useLocation } from 'react-router-dom'
import { Dialog, Transition } from '@headlessui/react'
import { Fragment } from 'react'
import {
  HomeIcon,
  LightBulbIcon,
  BuildingStorefrontIcon,
  NewspaperIcon,
  Cog6ToothIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline'
import clsx from 'clsx'
import LanguageSwitcher from './LanguageSwitcher'

const navigation = [
  { name: 'nav.dashboard', href: '/dashboard', icon: HomeIcon },
  { name: 'nav.recommendations', href: '/recommendations', icon: LightBulbIcon },
  { name: 'nav.business', href: '/business', icon: BuildingStorefrontIcon },
  { name: 'nav.news', href: '/news', icon: NewspaperIcon },
  { name: 'nav.settings', href: '/settings', icon: Cog6ToothIcon },
]

export default function Sidebar({ open, setOpen }) {
  const { t } = useTranslation()
  const location = useLocation()

  const SidebarContent = () => (
    <div className="flex h-full flex-col">
      <div className="flex h-16 flex-shrink-0 items-center px-4 bg-navitest-600">
        <h1 className="text-xl font-bold text-white">
          {t('app.name')}
        </h1>
      </div>
      <div className="flex flex-1 flex-col overflow-y-auto">
        <nav className="flex-1 space-y-1 px-2 py-4">
          {navigation.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.href
            
            return (
              <NavLink
                key={item.name}
                to={item.href}
                className={clsx(
                  isActive
                    ? 'bg-navitest-100 text-navitest-900'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900',
                  'group flex items-center px-2 py-2 text-sm font-medium rounded-md'
                )}
                onClick={() => setOpen(false)}
              >
                <Icon
                  className={clsx(
                    isActive ? 'text-navitest-500' : 'text-gray-400 group-hover:text-gray-500',
                    'mr-3 flex-shrink-0 h-6 w-6'
                  )}
                  aria-hidden="true"
                />
                {t(item.name)}
              </NavLink>
            )
          })}
        </nav>
        <div className="flex-shrink-0 p-4 border-t border-gray-200">
          <p className="text-xs text-gray-500 mb-2">
            {t('app.tagline')}
          </p>
          <div className="hidden lg:block">
            <LanguageSwitcher />
          </div>
        </div>
      </div>
    </div>
  )

  return (
    <>
      {/* Mobile sidebar */}
      <Transition.Root show={open} as={Fragment}>
        <Dialog as="div" className="relative z-40 lg:hidden" onClose={setOpen}>
          <Transition.Child
            as={Fragment}
            enter="transition-opacity ease-linear duration-300"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="transition-opacity ease-linear duration-300"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <div className="fixed inset-0 bg-gray-600 bg-opacity-75" />
          </Transition.Child>

          <div className="fixed inset-0 z-40 flex">
            <Transition.Child
              as={Fragment}
              enter="transition ease-in-out duration-300 transform"
              enterFrom="-translate-x-full"
              enterTo="translate-x-0"
              leave="transition ease-in-out duration-300 transform"
              leaveFrom="translate-x-0"
              leaveTo="-translate-x-full"
            >
              <Dialog.Panel className="relative flex w-full max-w-xs flex-1 flex-col bg-white">
                <Transition.Child
                  as={Fragment}
                  enter="ease-in-out duration-300"
                  enterFrom="opacity-0"
                  enterTo="opacity-100"
                  leave="ease-in-out duration-300"
                  leaveFrom="opacity-100"
                  leaveTo="opacity-0"
                >
                  <div className="absolute top-0 right-0 -mr-12 pt-2">
                    <button
                      type="button"
                      className="ml-1 flex h-10 w-10 items-center justify-center rounded-full focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white"
                      onClick={() => setOpen(false)}
                    >
                      <span className="sr-only">Close sidebar</span>
                      <XMarkIcon className="h-6 w-6 text-white" aria-hidden="true" />
                    </button>
                  </div>
                </Transition.Child>
                <SidebarContent />
              </Dialog.Panel>
            </Transition.Child>
            <div className="w-14 flex-shrink-0">{/* Force sidebar to shrink to fit close icon */}</div>
          </div>
        </Dialog>
      </Transition.Root>

      {/* Static sidebar for desktop */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
        <div className="flex min-h-0 flex-1 flex-col bg-white border-r border-gray-200">
          <SidebarContent />
        </div>
      </div>
    </>
  )
}