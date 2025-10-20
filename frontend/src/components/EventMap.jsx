import React from 'react'
import PropTypes from 'prop-types'
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'

// Fix for default marker icon in React Leaflet
// https://github.com/Leaflet/Leaflet/issues/4968
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
})

/**
 * EventMap Component
 *
 * Displays an event location on an interactive Leaflet map
 * Only renders if latitude and longitude are provided
 */
export default function EventMap({
  latitude,
  longitude,
  venueName,
  city,
  neighborhood,
  address,
  className = ''
}) {
  // Don't render if no coordinates
  if (!latitude || !longitude) {
    return null
  }

  // Validate coordinates
  const lat = parseFloat(latitude)
  const lng = parseFloat(longitude)

  if (isNaN(lat) || isNaN(lng)) {
    return (
      <div className={`bg-yellow-50 border border-yellow-200 rounded-lg p-4 ${className}`}>
        <p className="text-sm text-yellow-700">
          Coordenadas inválidas: {latitude}, {longitude}
        </p>
      </div>
    )
  }

  // Build location text for popup
  const locationParts = []
  if (venueName) locationParts.push(venueName)
  if (neighborhood) locationParts.push(neighborhood)
  if (city) locationParts.push(city)
  if (address) locationParts.push(address)
  const locationText = locationParts.join(', ')

  return (
    <div className={`rounded-lg overflow-hidden border border-gray-300 shadow-sm ${className}`}>
      <MapContainer
        center={[lat, lng]}
        zoom={15}
        style={{ height: '300px', width: '100%' }}
        scrollWheelZoom={false}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <Marker position={[lat, lng]}>
          <Popup>
            <div className="text-sm">
              <p className="font-bold mb-1">{venueName || 'Ubicación del evento'}</p>
              {locationText && <p className="text-gray-600">{locationText}</p>}
              <p className="text-xs text-gray-500 mt-2">
                {lat.toFixed(6)}, {lng.toFixed(6)}
              </p>
            </div>
          </Popup>
        </Marker>
      </MapContainer>
    </div>
  )
}

EventMap.propTypes = {
  latitude: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  longitude: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  venueName: PropTypes.string,
  city: PropTypes.string,
  neighborhood: PropTypes.string,
  address: PropTypes.string,
  className: PropTypes.string
}

EventMap.defaultProps = {
  latitude: null,
  longitude: null,
  venueName: null,
  city: null,
  neighborhood: null,
  address: null,
  className: ''
}
