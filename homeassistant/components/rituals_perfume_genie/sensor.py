"""Support for Rituals Perfume Genie sensors."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from pyrituals import Diffuser

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import RitualsDataUpdateCoordinator
from .entity import DiffuserEntity


@dataclass
class RitualsEntityDescriptionMixin:
    """Mixin values for Rituals entities."""

    value_fn: Callable[[Diffuser], int | str]


@dataclass
class RitualsSensorEntityDescription(
    SensorEntityDescription, RitualsEntityDescriptionMixin
):
    """Class describing Rituals sensor entities."""

    has_fn: Callable[[Diffuser], bool] = lambda _: True


ENTITY_DESCRIPTIONS = (
    RitualsSensorEntityDescription(
        key="battery_percentage",
        name="Battery",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        value_fn=lambda diffuser: diffuser.battery_percentage,
        has_fn=lambda diffuser: diffuser.has_battery,
    ),
    RitualsSensorEntityDescription(
        key="fill",
        name="Fill",
        icon="mdi:beaker",
        value_fn=lambda diffuser: diffuser.fill,
    ),
    RitualsSensorEntityDescription(
        key="perfume",
        name="Perfume",
        icon="mdi:tag",
        value_fn=lambda diffuser: diffuser.perfume,
    ),
    RitualsSensorEntityDescription(
        key="wifi_percentage",
        name="Wifi",
        icon="mdi:wifi",
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda diffuser: diffuser.wifi_percentage,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the diffuser sensors."""
    coordinators: dict[str, RitualsDataUpdateCoordinator] = hass.data[DOMAIN][
        config_entry.entry_id
    ]

    async_add_entities(
        RitualsSensorEntity(coordinator, description)
        for coordinator in coordinators.values()
        for description in ENTITY_DESCRIPTIONS
        if description.has_fn(coordinator.diffuser)
    )


class RitualsSensorEntity(DiffuserEntity, SensorEntity):
    """Representation of a diffuser sensor."""

    entity_description: RitualsSensorEntityDescription
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self,
        coordinator: RitualsDataUpdateCoordinator,
        description: RitualsSensorEntityDescription,
    ) -> None:
        """Initialize the diffuser sensor."""
        super().__init__(coordinator, description)
        self._attr_name = f"{coordinator.diffuser.name} {description.name}"

    @property
    def native_value(self) -> str | int:
        """Return the sensor value."""
        return self.entity_description.value_fn(self.coordinator.diffuser)
