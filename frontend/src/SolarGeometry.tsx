import React, { useState, useRef, useEffect } from 'react';
import 'ol/ol.css';
import Map from 'ol/Map';
import View from 'ol/View';
import TileLayer from 'ol/layer/Tile';
import OSM from 'ol/source/OSM';
import { fromLonLat, toLonLat } from 'ol/proj';
import { Feature } from 'ol';
import Point from 'ol/geom/Point';
import VectorLayer from 'ol/layer/Vector';
import VectorSource from 'ol/source/Vector';
import { Style, Icon } from 'ol/style';

const SolarGeometry: React.FC = () => {
  const [latitude, setLatitude] = useState('');
  const [longitude, setLongitude] = useState('');
  const [offset, setOffset] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const mapRef = useRef<HTMLDivElement | null>(null);
  const mapObj = useRef<Map | null>(null);
  const markerLayer = useRef<VectorLayer<VectorSource> | null>(null);

  useEffect(() => {
    if (!mapRef.current) return;
    if (!mapObj.current) {
      mapObj.current = new Map({
        target: mapRef.current,
        layers: [
          new TileLayer({ source: new OSM() })
        ],
        view: new View({
          center: fromLonLat([
            longitude ? parseFloat(longitude) : 0,
            latitude ? parseFloat(latitude) : 0
          ]),
          zoom: latitude && longitude ? 10 : 2
        })
      });
      mapObj.current.on('click', function (evt) {
        const coords = toLonLat(evt.coordinate);
        setLongitude(coords[0].toString());
        setLatitude(coords[1].toString());
      });
    } else {
      mapObj.current.setTarget(mapRef.current);
      mapObj.current.getView().setCenter(fromLonLat([
        longitude ? parseFloat(longitude) : 0,
        latitude ? parseFloat(latitude) : 0
      ]));
    }
    if (markerLayer.current) {
      mapObj.current.removeLayer(markerLayer.current);
    }
    if (latitude && longitude) {
      const marker = new Feature({
        geometry: new Point(fromLonLat([
          parseFloat(longitude),
          parseFloat(latitude)
        ]))
      });
      marker.setStyle(new Style({
        image: new Icon({
          anchor: [0.5, 1],
          src: 'https://openlayers.org/en/latest/examples/data/icon.png',
        })
      }));
      const vectorSource = new VectorSource({ features: [marker] });
      markerLayer.current = new VectorLayer({ source: vectorSource });
      mapObj.current.addLayer(markerLayer.current);
    }
    return () => {
      if (mapObj.current) mapObj.current.setTarget(undefined);
    };
  }, [latitude, longitude]);

  const handleFloatInputChange = (
    e: React.ChangeEvent<HTMLInputElement>,
    setter: React.Dispatch<React.SetStateAction<string>>
  ) => {
    const { value } = e.target;
    // Allow empty string, a single minus, or a valid float/partial float
    if (value === '' || value === '-' || /^-?\d*\.?\d*$/.test(value)) {
      setter(value);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const response = await fetch('/api/solar-geometry', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          latitude: latitude,
          longitude: longitude,
          offset: offset || null,
        }),
      });
      let data;
      try {
        data = await response.json();
      } catch {
        throw new Error('Response is not valid JSON');
      }
      if (!response.ok) throw new Error(data.error || 'Unknown error');
      setResult(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
      setSubmitted(true);
    }
  };

  return (
    <div>
      <h2>Solar Geometry</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>
            Latitude:
            <input
              type="text"
              inputMode="decimal"
              value={latitude}
              onChange={e => handleFloatInputChange(e, setLatitude)}
              required
            />
          </label>
        </div>
        <div>
          <label>
            Longitude:
            <input
              type="text"
              inputMode="decimal"
              value={longitude}
              onChange={e => handleFloatInputChange(e, setLongitude)}
              required
            />
          </label>
        </div>
        <div>
          <label>
            Offset Angle (optional):
            <input
              type="text"
              inputMode="decimal"
              value={offset}
              onChange={e => handleFloatInputChange(e, setOffset)}
            />
          </label>
        </div>
        <button type="submit" disabled={loading}>
          {loading ? 'Submitting...' : 'Submit'}
        </button>
      </form>
      <div ref={mapRef} style={{ height: '400px', width: '100%', marginBottom: '1em' }} />
      {submitted && (
        <div>
          <h3>Submitted Values</h3>
          <pre>{JSON.stringify({ latitude, longitude, offset }, null, 2)}</pre>
        </div>
      )}
      {result && (
        <div>
          <h3>Result from API</h3>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
      {error && <div style={{ color: 'red' }}>{error}</div>}
    </div>
  );
};

export default SolarGeometry; 