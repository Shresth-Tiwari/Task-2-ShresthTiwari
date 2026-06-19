from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields, validate, validates, ValidationError
from app.models import User


class UserSchema(SQLAlchemyAutoSchema):
    """Schema for serializing and deserializing User objects."""

    class Meta:
        model = User
        load_instance = True
        include_fk = True
        dump_only = ("id", "created_at", "updated_at")

    # Field-level validation
    username = fields.String(
        required=True,
        validate=[
            validate.Length(min=3, max=80, error="Username must be between 3 and 80 characters."),
            validate.Regexp(
                r"^[a-zA-Z0-9_.-]+$",
                error="Username may only contain letters, numbers, underscores, dots, and hyphens.",
            ),
        ],
    )
    email = fields.Email(required=True, validate=validate.Length(max=120))
    full_name = fields.String(load_default=None, validate=validate.Length(max=200))

    @validates("username")
    def validate_username_not_blank(self, value):
        if not value.strip():
            raise ValidationError("Username cannot be blank.")

    @validates("email")
    def validate_email_not_blank(self, value):
        if not value.strip():
            raise ValidationError("Email cannot be blank.")


# Reusable schema instances
user_schema = UserSchema()
users_schema = UserSchema(many=True)
user_update_schema = UserSchema(partial=True)  # All fields optional for PATCH-style PUT
