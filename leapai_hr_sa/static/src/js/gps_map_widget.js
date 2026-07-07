/*global L*/
/** @odoo-module **/

import { Component, useEffect, useRef } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardWidgetProps } from "@web/views/widgets/standard_widget_props";

/**
 * GPS Map Widget — shows a Leaflet map with a pin + geofence circle
 * on the hr.work.location.sa form view.
 *
 * Depends on: latitude, longitude, radius fields of the record.
 */
class GpsMapWidget extends Component {
    static template = "leapai_hr_sa.GpsMapWidget";
    static props = {
        ...standardWidgetProps,
    };

    // ── Lifecycle ──────────────────────────────────────────────────────────────

    setup() {
        this.mapRef = useRef("gps_map");
        this.leafletMap = null;
        this.marker = null;
        this.geofenceCircle = null;

        // Initialise the map once (empty deps array → runs once on mount).
        useEffect(
            () => {
                if (this.mapRef.el) {
                    this._initMap();
                }
                return () => {
                    if (this.leafletMap) {
                        this.leafletMap.remove();
                        this.leafletMap = null;
                        this.marker = null;
                        this.geofenceCircle = null;
                    }
                };
            },
            () => []
        );

        // Re-render pin + circle whenever coordinates change.
        useEffect(
            (lat, lng, radius) => {
                if (this.leafletMap) {
                    this._updateOverlays(lat, lng, radius);
                }
            },
            () => [
                this.props.record.data.latitude,
                this.props.record.data.longitude,
                this.props.record.data.radius,
            ]
        );
    }

    // ── Helpers ────────────────────────────────────────────────────────────────

    get lat() {
        return this.props.record.data.latitude || 0;
    }
    get lng() {
        return this.props.record.data.longitude || 0;
    }
    get radius() {
        return this.props.record.data.radius || 100;
    }
    get hasCoords() {
        return Boolean(this.lat || this.lng);
    }

    /**
     * Initialise the Leaflet map container and add the OSM tile layer.
     * Called once after the DOM element is available.
     */
    _initMap() {
        // Default centre: Riyadh, Saudi Arabia
        const center = this.hasCoords
            ? [this.lat, this.lng]
            : [24.7136, 46.6753];
        const zoom = this.hasCoords ? 15 : 6;

        this.leafletMap = L.map(this.mapRef.el, {
            scrollWheelZoom: false,
            zoomControl: true,
        });

        this.leafletMap.attributionControl.setPrefix(
            '<a href="https://leafletjs.com" title="Leaflet">Leaflet</a>'
        );

        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            maxZoom: 19,
            attribution:
                "&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a>",
        }).addTo(this.leafletMap);

        this.leafletMap.setView(center, zoom);

        if (this.hasCoords) {
            this._addOverlays(this.lat, this.lng, this.radius);
        }
    }

    /**
     * Remove existing marker + circle, add fresh ones at new coordinates.
     */
    _updateOverlays(lat, lng, radius) {
        if (this.marker) {
            this.leafletMap.removeLayer(this.marker);
            this.marker = null;
        }
        if (this.geofenceCircle) {
            this.leafletMap.removeLayer(this.geofenceCircle);
            this.geofenceCircle = null;
        }

        if (!lat && !lng) {
            return;
        }

        this._addOverlays(lat, lng, radius || 100);
        this.leafletMap.setView([lat, lng], this.leafletMap.getZoom() || 15, {
            animate: true,
        });
    }

    /**
     * Add a marker pin and a geofence circle to the map.
     */
    _addOverlays(lat, lng, radius) {
        this.marker = L.marker([lat, lng]).addTo(this.leafletMap);
        this.marker.bindPopup(
            `<strong>${this.props.record.data.name || ""}</strong><br/>` +
                `${lat.toFixed(6)}, ${lng.toFixed(6)}<br/>` +
                `Geofence: ${radius} m`
        );

        this.geofenceCircle = L.circle([lat, lng], {
            radius: radius,
            color: "#006C35",
            weight: 2,
            fillColor: "#006C35",
            fillOpacity: 0.15,
        }).addTo(this.leafletMap);
    }
}

// ── Registry registration ──────────────────────────────────────────────────────

export const gpsMapWidget = {
    component: GpsMapWidget,
    fieldDependencies: [
        { name: "latitude", type: "float" },
        { name: "longitude", type: "float" },
        { name: "radius", type: "float" },
    ],
};

registry.category("view_widgets").add("gps_map", gpsMapWidget);
