"""Pydantic schema for CustomField Response"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class CustomFieldResponse(BaseModel):
    """CustomField response schema"""

    gid: Optional[str] = Field(description="Globally unique identifier of the resource, as a string.", example='12345')
    resource_type: Optional[str] = Field(description="The base type of this resource.", example='custom_field')
    name: Optional[str] = Field(description="The name of the custom field.", example='Status')
    type: Optional[str] = Field(description="*Deprecated: new integrations should prefer the resource_subtype field.* The type of the custom field. Must be one of the given values.")
    enum_options: Optional[List[dict]] = Field(description="*Conditional*. Only relevant for custom fields of type `enum` or `multi_enum`. This array specifies the possible values which an `enum` custom field can adopt. To modify the enum options, refer to [working with enum options](/reference/createenumoptionforcustomfield).")
    enabled: Optional[bool] = Field(description="*Conditional*. This field applies only to [custom field values](/docs/custom-fields-guide#/accessing-custom-field-values-on-tasks-or-projects) and is not available for [custom field definitions](/docs/custom-fields-guide#/accessing-custom-field-definitions). Determines if the custom field is enabled or not. For more details, see the [Custom Fields documentation](/docs/custom-fields-guide#/enabled-and-disabled-values).", example=True)
    representation_type: Optional[str] = Field(description="This field tells the type of the custom field.", example='number')
    id_prefix: Optional[str] = Field(description="This field is the unique custom ID string for the custom field.", example='ID')
    input_restrictions: Optional[List[str]] = Field(description="*Conditional*. Only relevant for custom fields of type `reference`. This array of strings reflects the allowed types of objects that can be written to a `reference` custom field value.", example='task')
    is_formula_field: Optional[bool] = Field(description="*Conditional*. This flag describes whether a custom field is a formula custom field.", example=False)
    date_value: Optional[dict] = Field(description="*Conditional*. Only relevant for custom fields of type `date`. This object reflects the chosen date (and optionally, time) value of a `date` custom field. If no date is selected, the value of `date_value` will be `null`.")
    enum_value: Optional[dict] = None
    multi_enum_values: Optional[List[dict]] = Field(description="*Conditional*. Only relevant for custom fields of type `multi_enum`. This object is the chosen values of a `multi_enum` custom field.")
    number_value: Optional[float] = Field(description="*Conditional*. This number is the value of a `number` custom field.", example=5.2)
    text_value: Optional[str] = Field(description="*Conditional*. This string is the value of a `text` custom field.", example='Some Value')
    display_value: Optional[str] = Field(description="A string representation for the value of the custom field. Integrations that don't require the underlying type should use this field to read values. Using this field will future-proof an app against new custom field types.", example='blue')
    description: Optional[str] = Field(description="[Opt In](/docs/inputoutput-options). The description of the custom field.", example='Development team priority')
    precision: Optional[int] = Field(description="Only relevant for custom fields of type `Number`. This field dictates the number of places after the decimal to round to, i.e. 0 is integer values, 1 rounds to the nearest tenth, and so on. Must be between 0 and 6, inclusive. For percentage format, this may be unintuitive, as a value of 0.25 has a precision of 0, while a value of 0.251 has a precision of 1. This is due to 0.25 being displayed as 25%. The identifier format will always have a precision of 0.", example=2)
    format: Optional[str] = Field(description="The format of this custom field.", example='custom')
    currency_code: Optional[str] = Field(description="ISO 4217 currency code to format this custom field. This will be null if the `format` is not `currency`.", example='EUR')
    custom_label: Optional[str] = Field(description="This is the string that appears next to the custom field value. This will be null if the `format` is not `custom`.", example='gold pieces')
    custom_label_position: Optional[str] = Field(description="Only relevant for custom fields with `custom` format. This depicts where to place the custom label. This will be null if the `format` is not `custom`.", example='suffix')
    is_global_to_workspace: Optional[bool] = Field(description="This flag describes whether this custom field is available to every container in the workspace. Before project-specific custom fields, this field was always true.", example=True)
    has_notifications_enabled: Optional[bool] = Field(description="*Conditional*. This flag describes whether a follower of a task with this field should receive inbox notifications from changes to this field.", example=True)
    asana_created_field: Optional[str] = Field(description="*Conditional*. A unique identifier to associate this field with the template source of truth.", example='priority')
    is_value_read_only: Optional[bool] = Field(description="*Conditional*. This flag describes whether a custom field is read only.", example=False)
    created_by: Optional['UserCompact'] = None
    people_value: Optional[List['UserCompact']] = Field(description="*Conditional*. Only relevant for custom fields of type `people`. This array of [compact user](/reference/users) objects reflects the values of a `people` custom field.")
    reference_value: Optional[List[dict]] = Field(description="*Conditional*. Only relevant for custom fields of type `reference`. This array of objects reflects the values of a `reference` custom field.")
    privacy_setting: Optional[str] = Field(description="The privacy setting of the custom field. *Note: Administrators in your organization may restrict the values of `privacy_setting`.*", example='public_with_guests')
    default_access_level: Optional[str] = Field(description="The default access level when inviting new members to the custom field. This isn't applied when the `privacy_setting` is `private`, or the user is a guest. For local fields in a project or portfolio, the user must additionally have permission to modify the container itself.", example='user')
    resource_subtype: Optional[str] = Field(description="The type of the custom field. Must be one of the given values.", example='text')

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "gid": "12345",
                "resource_type": "custom_field",
                "name": "Example Name"
            }
        }

"""Pydantic schema for CustomField Compact (nested)"""
from pydantic import BaseModel, Field
from typing import Optional


class CustomFieldCompact(BaseModel):
    """CustomField compact schema for nested responses"""

    gid: Optional[str] = Field(description="Globally unique identifier of the resource, as a string.")
    resource_type: Optional[str] = Field(description="The base type of this resource.")
    name: str = Field(description="The name of the custom field.")

    class Config:
        from_attributes = True

"""Pydantic schema for CustomField Create Request"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class CustomFieldCreate(BaseModel):
    """CustomField create request schema"""

    name: Optional[str] = Field(None, description="The name of the custom field.")
    enum_options: Optional[List[dict]] = Field(None, description="*Conditional*. Only relevant for custom fields of type `enum` or `multi_enum`. This array specifies the possible values which an `enum` custom field can adopt. To modify the enum options, refer to [working with enum options](/reference/createenumoptionforcustomfield).")
    id_prefix: Optional[str] = Field(None, description="This field is the unique custom ID string for the custom field.")
    input_restrictions: Optional[List[str]] = Field(None, description="*Conditional*. Only relevant for custom fields of type `reference`. This array of strings reflects the allowed types of objects that can be written to a `reference` custom field value.")
    is_formula_field: Optional[bool] = Field(None, description="*Conditional*. This flag describes whether a custom field is a formula custom field.")
    date_value: Optional[dict] = Field(None, description="*Conditional*. Only relevant for custom fields of type `date`. This object reflects the chosen date (and optionally, time) value of a `date` custom field. If no date is selected, the value of `date_value` will be `null`.")
    enum_value: Optional[dict] = None
    multi_enum_values: Optional[List[dict]] = Field(None, description="*Conditional*. Only relevant for custom fields of type `multi_enum`. This object is the chosen values of a `multi_enum` custom field.")
    number_value: Optional[float] = Field(None, description="*Conditional*. This number is the value of a `number` custom field.")
    text_value: Optional[str] = Field(None, description="*Conditional*. This string is the value of a `text` custom field.")
    description: Optional[str] = Field(None, description="[Opt In](/docs/inputoutput-options). The description of the custom field.")
    precision: Optional[int] = Field(None, description="Only relevant for custom fields of type `Number`. This field dictates the number of places after the decimal to round to, i.e. 0 is integer values, 1 rounds to the nearest tenth, and so on. Must be between 0 and 6, inclusive. For percentage format, this may be unintuitive, as a value of 0.25 has a precision of 0, while a value of 0.251 has a precision of 1. This is due to 0.25 being displayed as 25%. The identifier format will always have a precision of 0.")
    format: Optional[str] = Field(None, description="The format of this custom field.")
    currency_code: Optional[str] = Field(None, description="ISO 4217 currency code to format this custom field. This will be null if the `format` is not `currency`.")
    custom_label: Optional[str] = Field(None, description="This is the string that appears next to the custom field value. This will be null if the `format` is not `custom`.")
    custom_label_position: Optional[str] = Field(None, description="Only relevant for custom fields with `custom` format. This depicts where to place the custom label. This will be null if the `format` is not `custom`.")
    has_notifications_enabled: Optional[bool] = Field(None, description="*Conditional*. This flag describes whether a follower of a task with this field should receive inbox notifications from changes to this field.")
    is_value_read_only: Optional[bool] = Field(None, description="*Conditional*. This flag describes whether a custom field is read only.")
    created_by: Optional['UserCompact'] = None
    people_value: Optional[List['UserCompact']] = Field(None, description="*Conditional*. Only relevant for custom fields of type `people`. This array of [compact user](/reference/users) objects reflects the values of a `people` custom field.")
    reference_value: Optional[List[dict]] = Field(None, description="*Conditional*. Only relevant for custom fields of type `reference`. This array of objects reflects the values of a `reference` custom field.")
    privacy_setting: Optional[str] = Field(None, description="The privacy setting of the custom field. *Note: Administrators in your organization may restrict the values of `privacy_setting`.*")
    default_access_level: Optional[str] = Field(None, description="The default access level when inviting new members to the custom field. This isn't applied when the `privacy_setting` is `private`, or the user is a guest. For local fields in a project or portfolio, the user must additionally have permission to modify the container itself.")

    class Config:
        from_attributes = True

"""Pydantic schema for CustomField Update Request"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class CustomFieldUpdate(BaseModel):
    """CustomField update request schema"""

    name: Optional[str] = Field(None, description="The name of the custom field.")
    enum_options: Optional[List[dict]] = Field(None, description="*Conditional*. Only relevant for custom fields of type `enum` or `multi_enum`. This array specifies the possible values which an `enum` custom field can adopt. To modify the enum options, refer to [working with enum options](/reference/createenumoptionforcustomfield).")
    id_prefix: Optional[str] = Field(None, description="This field is the unique custom ID string for the custom field.")
    input_restrictions: Optional[List[str]] = Field(None, description="*Conditional*. Only relevant for custom fields of type `reference`. This array of strings reflects the allowed types of objects that can be written to a `reference` custom field value.")
    is_formula_field: Optional[bool] = Field(None, description="*Conditional*. This flag describes whether a custom field is a formula custom field.")
    date_value: Optional[dict] = Field(None, description="*Conditional*. Only relevant for custom fields of type `date`. This object reflects the chosen date (and optionally, time) value of a `date` custom field. If no date is selected, the value of `date_value` will be `null`.")
    enum_value: Optional[dict] = None
    multi_enum_values: Optional[List[dict]] = Field(None, description="*Conditional*. Only relevant for custom fields of type `multi_enum`. This object is the chosen values of a `multi_enum` custom field.")
    number_value: Optional[float] = Field(None, description="*Conditional*. This number is the value of a `number` custom field.")
    text_value: Optional[str] = Field(None, description="*Conditional*. This string is the value of a `text` custom field.")
    description: Optional[str] = Field(None, description="[Opt In](/docs/inputoutput-options). The description of the custom field.")
    precision: Optional[int] = Field(None, description="Only relevant for custom fields of type `Number`. This field dictates the number of places after the decimal to round to, i.e. 0 is integer values, 1 rounds to the nearest tenth, and so on. Must be between 0 and 6, inclusive. For percentage format, this may be unintuitive, as a value of 0.25 has a precision of 0, while a value of 0.251 has a precision of 1. This is due to 0.25 being displayed as 25%. The identifier format will always have a precision of 0.")
    format: Optional[str] = Field(None, description="The format of this custom field.")
    currency_code: Optional[str] = Field(None, description="ISO 4217 currency code to format this custom field. This will be null if the `format` is not `currency`.")
    custom_label: Optional[str] = Field(None, description="This is the string that appears next to the custom field value. This will be null if the `format` is not `custom`.")
    custom_label_position: Optional[str] = Field(None, description="Only relevant for custom fields with `custom` format. This depicts where to place the custom label. This will be null if the `format` is not `custom`.")
    has_notifications_enabled: Optional[bool] = Field(None, description="*Conditional*. This flag describes whether a follower of a task with this field should receive inbox notifications from changes to this field.")
    is_value_read_only: Optional[bool] = Field(None, description="*Conditional*. This flag describes whether a custom field is read only.")
    created_by: Optional['UserCompact'] = None
    people_value: Optional[List['UserCompact']] = Field(None, description="*Conditional*. Only relevant for custom fields of type `people`. This array of [compact user](/reference/users) objects reflects the values of a `people` custom field.")
    reference_value: Optional[List[dict]] = Field(None, description="*Conditional*. Only relevant for custom fields of type `reference`. This array of objects reflects the values of a `reference` custom field.")
    privacy_setting: Optional[str] = Field(None, description="The privacy setting of the custom field. *Note: Administrators in your organization may restrict the values of `privacy_setting`.*")
    default_access_level: Optional[str] = Field(None, description="The default access level when inviting new members to the custom field. This isn't applied when the `privacy_setting` is `private`, or the user is a guest. For local fields in a project or portfolio, the user must additionally have permission to modify the container itself.")

    class Config:
        from_attributes = True