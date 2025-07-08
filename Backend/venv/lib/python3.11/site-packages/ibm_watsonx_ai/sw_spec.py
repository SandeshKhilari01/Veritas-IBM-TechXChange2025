#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2023-2025.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------

from __future__ import annotations
import json
from typing import Any, TYPE_CHECKING
from warnings import warn

import ibm_watsonx_ai._wrappers.requests as requests
from ibm_watsonx_ai.lifecycle import SpecStates
from ibm_watsonx_ai.metanames import SwSpecMetaNames
from ibm_watsonx_ai.utils import SW_SPEC_DETAILS_TYPE
from ibm_watsonx_ai.utils.utils import _get_id_from_deprecated_uid
from ibm_watsonx_ai.wml_client_error import WMLClientError, ResourceIdByNameNotFound
from ibm_watsonx_ai.wml_resource import WMLResource


if TYPE_CHECKING:
    from ibm_watsonx_ai import APIClient
    from pandas import DataFrame


class SwSpec(WMLResource):
    """Store and manage software specs."""

    ConfigurationMetaNames = SwSpecMetaNames()
    """MetaNames for Software Specification creation."""

    def __init__(self, client: APIClient):
        WMLResource.__init__(self, __name__, client)
        self.software_spec_list = None

    def get_details(
        self, sw_spec_id: str | None = None, state_info: bool = False, **kwargs: Any
    ) -> dict[str, Any]:
        """Get software specification details. If no sw_spec_id is passed, details for all software specifications
        are returned.

        :param sw_spec_id: ID of the software specification
        :type sw_spec_id: str, optional

        :param state_info: works only when `sw_spec_id` is None, instead of returning details of software specs, it returns
            the state of the software specs information (supported, unsupported, deprecated), containing suggested replacement
            in case of unsupported or deprecated software specs
        :type sw_spec_id: bool

        :return: metadata of the stored software specification(s)
        :rtype:
          - **dict** - if `sw_spec_uid` is not None
          - **{"resources": [dict]}** - if `sw_spec_uid` is None

        **Examples**

        .. code-block:: python

            sw_spec_details = client.software_specifications.get_details(sw_spec_uid)
            sw_spec_details = client.software_specifications.get_details()
            sw_spec_state_details = client.software_specifications.get_details(state_info=True)

        """
        sw_spec_id = _get_id_from_deprecated_uid(
            kwargs, sw_spec_id, "sw_spec", can_be_none=True
        )

        SwSpec._validate_type(sw_spec_id, "sw_spec_id", str, False)

        if sw_spec_id:
            response = requests.get(
                self._client._href_definitions.get_sw_spec_href(sw_spec_id),
                params=self._client._params(skip_space_project_chk=True),
                headers=self._client._get_headers(),
            )

            if response.status_code == 200:
                return self._get_required_element_from_response(
                    self._handle_response(200, "get sw spec details", response)
                )
            else:
                return self._handle_response(200, "get sw spec details", response)
        else:
            if state_info:
                response = requests.get(
                    self._client._href_definitions.get_sw_specs_href(),
                    params=self._client._params(),
                    headers=self._client._get_headers(),
                )

                return self._handle_response(200, "get sw specs details", response)
            else:
                response = requests.get(
                    self._client._href_definitions.get_sw_specs_href(),
                    params=self._client._params(
                        skip_space_project_chk=self._client.ICP_PLATFORM_SPACES
                    ),
                    headers=self._client._get_headers(),
                )

                return {
                    "resources": [
                        self._get_required_element_from_response(x)
                        for x in self._handle_response(
                            200, "get sw specs details", response
                        )["resources"]
                    ]
                }

    def store(self, meta_props: dict) -> dict:
        """Create a software specification.

        :param meta_props: metadata of the space configuration. To see available meta names, use:

            .. code-block:: python

                client.software_specifications.ConfigurationMetaNames.get()

        :type meta_props: dict

        :return: metadata of the stored space
        :rtype: dict

        **Example:**

        .. code-block:: python

            meta_props = {
                client.software_specifications.ConfigurationMetaNames.NAME: "skl_pipeline_heart_problem_prediction",
                client.software_specifications.ConfigurationMetaNames.DESCRIPTION: "description scikit-learn_0.20",
                client.software_specifications.ConfigurationMetaNames.PACKAGE_EXTENSIONS: [],
                client.software_specifications.ConfigurationMetaNames.SOFTWARE_CONFIGURATION: {},
                client.software_specifications.ConfigurationMetaNames.BASE_SOFTWARE_SPECIFICATION: {"guid": "<guid>"}
            }

            sw_spec_details = client.software_specifications.store(meta_props)

        """
        SwSpec._validate_type(meta_props, "meta_props", dict, True)
        sw_spec_meta = self.ConfigurationMetaNames._generate_resource_metadata(
            meta_props, with_validation=True, client=self._client
        )

        sw_spec_meta_json = json.dumps(sw_spec_meta)
        href = self._client._href_definitions.get_sw_specs_href()

        creation_response = requests.post(
            href,
            params=self._client._params(),
            headers=self._client._get_headers(),
            data=sw_spec_meta_json,
        )

        sw_spec_details = self._handle_response(
            201, "creating sofware specifications", creation_response
        )

        return sw_spec_details

    def list(
        self, limit: int | None = None, spec_states: list[SpecStates] | None = None
    ) -> DataFrame:
        """List software specifications in a table format.

        :param limit: limit number of fetched records
        :type limit: int, optional

        :param spec_states: specification state filter, by default shows available, supported and custom software specifications
        :type spec_states: list[SpecStates], optional

        :return: pandas.DataFrame with listed software specifications
        :rtype: pandas.DataFrame

        **Example:**

        .. code-block:: python

            client.software_specifications.list()
        """
        if spec_states is None:
            spec_states = [SpecStates.SUPPORTED, SpecStates.AVAILABLE, ""]

        spec_states = [s.value if isinstance(s, SpecStates) else s for s in spec_states]

        asset_details = self.get_details(state_info=True)

        sw_spec_values = [
            (
                m["metadata"]["name"],
                m["metadata"]["asset_id"],
                m["entity"]["software_specification"].get("type", "derived"),
                self._get_spec_state(m),
                m["metadata"].get("life_cycle", {}).get("replacement_name", ""),
            )
            for m in asset_details["resources"]
            if self._get_spec_state(m) in spec_states
        ]
        table = self._list(
            sw_spec_values,
            ["NAME", "ID", "TYPE", "STATE", "REPLACEMENT"],
            limit,
        )

        return table

    @staticmethod
    def get_id(sw_spec_details: dict) -> str:
        """Get the unique ID of a software specification.

        :param sw_spec_details: metadata of the software specification
        :type sw_spec_details: dict

        :return: unique ID of the software specification
        :rtype: str

        **Example:**

        .. code-block:: python

            asset_id = client.software_specifications.get_id(sw_spec_details)

        """
        SwSpec._validate_type(sw_spec_details, "sw_spec_details", object, True)
        SwSpec._validate_type_of_details(sw_spec_details, SW_SPEC_DETAILS_TYPE)

        return WMLResource._get_required_element_from_dict(
            sw_spec_details, "sw_spec_details", ["metadata", "asset_id"]
        )

    @staticmethod
    def get_uid(sw_spec_details: dict) -> str:
        """Get the unique ID of a software specification.

        *Deprecated:* Use ``get_id(sw_spec_details)`` instead.

        :param sw_spec_details: metadata of the software specification
        :type sw_spec_details: dict

        :return: unique ID of the software specification
        :rtype: str

        **Example:**

        .. code-block:: python

            asset_uid = client.software_specifications.get_uid(sw_spec_details)

        """
        get_uid_method_deprecated_warning = (
            "This method is deprecated, please use `get_id(sw_spec_details)` instead"
        )
        warn(get_uid_method_deprecated_warning, category=DeprecationWarning)
        return SwSpec.get_id(sw_spec_details)

    def get_id_by_name(self, sw_spec_name: str) -> str:
        """Get the unique ID of a software specification.

        :param sw_spec_name: name of the software specification
        :type sw_spec_name: str

        :return: unique ID of the software specification
        :rtype: str

        **Example:**

        .. code-block:: python

            asset_uid = client.software_specifications.get_id_by_name(sw_spec_name)

        """

        SwSpec._validate_type(sw_spec_name, "sw_spec_name", str, True)
        parameters = self._client._params(skip_space_project_chk=True)
        parameters.update(name=sw_spec_name)

        response = requests.get(
            self._client._href_definitions.get_sw_specs_href(),
            params=parameters,
            headers=self._client._get_headers(),
        )

        total_values = self._handle_response(200, "list assets", response)[
            "total_results"
        ]
        if total_values != 0:
            sw_spec_details = self._handle_response(200, "list assets", response)[
                "resources"
            ]
            return sw_spec_details[0]["metadata"]["asset_id"]
        else:
            raise ResourceIdByNameNotFound(sw_spec_name, "software spec")

    def get_uid_by_name(self, sw_spec_name: str) -> str:
        """Get the unique ID of a software specification.

        *Deprecated:* Use ``get_id_by_name(self, sw_spec_name)`` instead.

        :param sw_spec_name: name of the software specification
        :type sw_spec_name: str

        :return: unique ID of the software specification
        :rtype: str

        **Example:**

        .. code-block:: python

            asset_uid = client.software_specifications.get_uid_by_name(sw_spec_name)

        """
        get_uid_by_name_method_deprecated_warning = "This method is deprecated, please use `get_id_by_name(sw_spec_name)` instead"
        warn(get_uid_by_name_method_deprecated_warning, category=DeprecationWarning)
        return SwSpec.get_id_by_name(self, sw_spec_name)

    @staticmethod
    def get_href(sw_spec_details: dict) -> str:
        """Get the URL of a software specification.

        :param sw_spec_details: details of the software specification
        :type sw_spec_details: dict

        :return: href of the software specification
        :rtype: str

        **Example:**

        .. code-block:: python

            sw_spec_details = client.software_specifications.get_details(sw_spec_id)
            sw_spec_href = client.software_specifications.get_href(sw_spec_details)

        """
        SwSpec._validate_type(sw_spec_details, "sw_spec_details", object, True)
        SwSpec._validate_type_of_details(sw_spec_details, SW_SPEC_DETAILS_TYPE)

        return WMLResource._get_required_element_from_dict(
            sw_spec_details, "sw_spec_details", ["metadata", "href"]
        )

    def delete(self, sw_spec_id: str | None = None, **kwargs: Any) -> str:
        """Delete a software specification.

        :param sw_spec_id: unique ID of the software specification
        :type sw_spec_id: str

        :return: status ("SUCCESS" or "FAILED")
        :rtype: str

        **Example:**

        .. code-block:: python

            client.software_specifications.delete(sw_spec_id)

        """
        sw_spec_id = _get_id_from_deprecated_uid(
            kwargs, sw_spec_id, "sw_spec", can_be_none=False
        )
        SwSpec._validate_type(sw_spec_id, "sw_spec_id", str, True)

        response = requests.delete(
            self._client._href_definitions.get_sw_spec_href(sw_spec_id),
            params=self._client._params(),
            headers=self._client._get_headers(),
        )

        if response.status_code == 200:
            return self._get_required_element_from_response(response.json())  # type: ignore
        else:
            return self._handle_response(204, "delete software specification", response)

    def add_package_extension(
        self,
        sw_spec_id: str | None = None,
        pkg_extn_id: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Add a package extension to a software specification's existing metadata.

        :param sw_spec_id: unique ID of the software specification to be updated
        :type sw_spec_id: str

        :param pkg_extn_id: unique ID of the package extension to be added to the software specification
        :type pkg_extn_id: str

        :return: status
        :rtype: str

        **Example:**

        .. code-block:: python

            client.software_specifications.add_package_extension(sw_spec_id, pkg_extn_id)

        """
        if pkg_extn_id is None:
            raise TypeError(
                "add_package_extension() missing 1 required positional argument: 'pkg_extn_id'"
            )
        sw_spec_id = _get_id_from_deprecated_uid(
            kwargs, sw_spec_id, "sw_spec", can_be_none=False
        )

        ##For CP4D, check if either spce or project ID is set
        self._client._check_if_either_is_set()

        self._validate_type(sw_spec_id, "sw_spec_id", str, True)
        self._validate_type(pkg_extn_id, "pkg_extn_id", str, True)

        url = self._client._href_definitions.get_sw_spec_href(sw_spec_id)

        url = url + "/package_extensions/" + pkg_extn_id

        response = requests.put(
            url, params=self._client._params(), headers=self._client._get_headers()
        )

        if response.status_code == 204:
            print("SUCCESS")
            return "SUCCESS"
        else:
            return self._handle_response(204, "pkg spec add", response, False)

    def delete_package_extension(
        self,
        sw_spec_id: str | None = None,
        pkg_extn_id: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Delete a package extension from a software specification's existing metadata.

        :param sw_spec_id: unique ID of the software specification to be updated
        :type sw_spec_id: str

        :param pkg_extn_id: unique ID of the package extension to be deleted from the software specification
        :type pkg_extn_id: str

        :return: status
        :rtype: str

        **Example:**

        .. code-block:: python

            client.software_specifications.delete_package_extension(sw_spec_uid, pkg_extn_id)

        """
        if pkg_extn_id is None:
            raise TypeError(
                "add_package_extension() missing 1 required positional argument: 'pkg_extn_id'"
            )
        sw_spec_id = _get_id_from_deprecated_uid(
            kwargs, sw_spec_id, "sw_spec", can_be_none=False
        )

        ##For CP4D, check if either spce or project ID is set
        self._client._check_if_either_is_set()

        self._validate_type(sw_spec_id, "sw_spec_id", str, True)
        self._validate_type(pkg_extn_id, "pkg_extn_id", str, True)

        url = self._client._href_definitions.get_sw_spec_href(sw_spec_id)

        url = url + "/package_extensions/" + pkg_extn_id

        response = requests.delete(
            url, params=self._client._params(), headers=self._client._get_headers()
        )

        return self._handle_response(204, "pkg spec delete", response, False)

    @staticmethod
    def _get_spec_state(spec_details: dict) -> str:
        if spec_details["entity"].get("software_specification").get("type") != "base":
            return ""
        elif "life_cycle" not in spec_details["metadata"]:
            return (
                SpecStates.SUPPORTED.value
            )  # if no lifecycle info in the metadata, then we should assume it is supported
        elif SpecStates.RETIRED.value in spec_details["metadata"]["life_cycle"]:
            return SpecStates.RETIRED.value
        elif SpecStates.CONSTRICTED.value in spec_details["metadata"]["life_cycle"]:
            return SpecStates.CONSTRICTED.value
        elif SpecStates.DEPRECATED.value in spec_details["metadata"]["life_cycle"]:
            return SpecStates.DEPRECATED.value
        else:
            for state in SpecStates:
                if state.value in spec_details["metadata"]["life_cycle"]:
                    return state.value

            return (
                SpecStates.SUPPORTED.value
            )  # when no other info in lifecycle, then we should assume it is supported

    def _get_required_element_from_response(
        self, response_data: dict[str, Any]
    ) -> dict:

        WMLResource._validate_type(response_data, "sw_spec_response", dict)
        try:
            new_el = {
                "metadata": {
                    "name": response_data["metadata"]["name"],
                    "asset_id": response_data["metadata"]["asset_id"],
                    "href": response_data["metadata"]["href"],
                    "asset_type": response_data["metadata"]["asset_type"],
                    "created_at": response_data["metadata"]["created_at"],
                },
                "entity": response_data["entity"],
            }
            if "life_cycle" in response_data["metadata"]:
                new_el["metadata"]["life_cycle"] = response_data["metadata"][
                    "life_cycle"
                ]
            if "href" in response_data["metadata"]:
                href_without_host = response_data["metadata"]["href"].split(".com")[-1]
                new_el["metadata"].update({"href": href_without_host})
            return new_el
        except Exception:
            raise WMLClientError(
                "Failed to read Response from down-stream service: "
                + str(response_data)
            )

    def _get_state_info(self) -> tuple[dict, dict]:
        spec_details = self.get_details(state_info=True)

        state_info_by_id = {
            s["metadata"].get("asset_id"): {
                "state": self._get_spec_state(s),
                "replacement": s["metadata"]
                .get("life_cycle", {})
                .get("replacement_name", ""),
            }
            for s in spec_details["resources"]
        }

        state_info_by_name = {
            s["metadata"].get("name"): {
                "state": self._get_spec_state(s),
                "replacement": s["metadata"]
                .get("life_cycle", {})
                .get("replacement_name", ""),
            }
            for s in spec_details["resources"]
        }

        return state_info_by_id, state_info_by_name

    def _get_info(self, asset_details) -> dict | None:
        if not hasattr(self, "_spec_info"):
            self._spec_info = self._get_state_info()

        if (
            sw_spec_id := asset_details.get("entity", {})
            .get("software_spec", {})
            .get("id")
        ) is not None:
            return self._spec_info[0].get(sw_spec_id)
        elif (
            sw_spec_name := asset_details.get("entity", {})
            .get("software_spec", {})
            .get("name")
        ) is not None:
            return self._spec_info[1].get(sw_spec_name)

    def _get_state(self, asset_details) -> str:
        spec_info = self._get_info(asset_details)

        if spec_info:
            return spec_info.get("state", "")
        else:
            return "not_provided"

    def _get_replacement(self, asset_details) -> str:
        spec_info = self._get_info(asset_details)

        if spec_info:
            return spec_info.get("replacement", "")
        else:
            return ""
