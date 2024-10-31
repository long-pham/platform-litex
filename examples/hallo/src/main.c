
#include <stdio.h>
#include <zephyr/kernel.h>
// #include "csr.h"
#include <zephyr/drivers/gpio.h>

/* 1000 msec = 1 sec */
#define SLEEP_TIME_MS   1000

/* The devicetree node identifier for the "led0" alias. */
// #define LED_NODE DT_ALIAS(led0)

/*
 * A build error on this line means your board is unsupported.
 * See the sample documentation for information on how to fix this.
 */
// static const struct gpio_dt_spec led = GPIO_DT_SPEC_GET(LED_NODE, gpios);

int main(void)
{
	// int ret;
	bool led_state = true;
	uint64_t count=0;

	// if (!gpio_is_ready_dt(&led)) {
	// 	return 0;
	// }

	// ret = gpio_pin_configure_dt(&led, GPIO_OUTPUT_ACTIVE);
	// if (ret < 0) {
	// 	return 0;
	// }
	// uint32_t *reg = (uint32_t*)0xe0002000;
	printf("IDENTIFIER_MEM: %x\n", *(uint32_t*)0xe0002000);

	// printf("gitrev: %x\n", version_gitrev_read());

	while (1) {
		// ret = gpio_pin_toggle_dt(&led);
		// if (ret < 0) {
		// 	return 0;
		// }

		led_state = !led_state;
		// leds_out_write(led_state);
		// printf("%llu - LED state: %s\n", count++, led_state ? "ON" : "OFF");

		// k_msleep(SLEEP_TIME_MS);
	}
	return 0;
}

