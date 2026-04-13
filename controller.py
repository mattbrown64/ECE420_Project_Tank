import pygame


def main() -> None:
    pygame.init()
    pygame.joystick.init()

    try:
        count = pygame.joystick.get_count()
        if count == 0:
            print("No controllers found.")
            return

        print(f"Controllers detected: {count}")
        for index in range(count):
            joystick = pygame.joystick.Joystick(index)
            joystick.init()

            name = joystick.get_name()
            axes = joystick.get_numaxes()
            buttons = joystick.get_numbuttons()
            hats = joystick.get_numhats()
            guid = joystick.get_guid() if hasattr(joystick, "get_guid") else "unknown"
            instance_id = (
                joystick.get_instance_id() if hasattr(joystick, "get_instance_id") else "unknown"
            )

            print("-")
            print(f"Index: {index}")
            print(f"Name: {name}")
            print(f"GUID: {guid}")
            print(f"Instance ID: {instance_id}")
            print(f"Axes: {axes}")
            print(f"Buttons: {buttons}")
            print(f"Hats: {hats}")
    finally:
        pygame.joystick.quit()
        pygame.quit()


if __name__ == "__main__":
    main()
