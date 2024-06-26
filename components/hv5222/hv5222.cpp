#include "hv5222.h"
#include "esphome/core/log.h"
// #include <sstream>
// #include <string>
// #include <iomanip>

namespace esphome {
  namespace hv5222 {

    static const char* const TAG = "HV5222";

    void HV5222component::setup() {
      ESP_LOGD(TAG, "Setting up HV5222 via SPI bus...");
      this->spi_setup();
      this->latch_pin_->setup();
      this->latch_pin_->digital_write(false);
      this->write_bytes();
    }

    void HV5222component::dump_config() { ESP_LOGCONFIG(TAG, "HV5222:"); }

    void HV5222component::digital_write_(uint16_t pin, bool value) {
      if (pin > this->max_pins_ * 8) {
        ESP_LOGE(TAG, "Pin %u is out of range! Maximum pin number with %u chips is %u.", pin, this->chip_count_,
          (this->max_pins_ * 8));
        return;
      }
      if (value) {
        this->output_bytes_[(this->max_pins_) - (pin / 8) - 1] |= (1 << (pin % 8));
      }
      else {
        this->output_bytes_[(this->max_pins_) - (pin / 8) - 1] &= ~(1 << (pin % 8));
      }
      this->write_bytes();
    }

    void HV5222component::write_bytes() {
#ifdef ESP_LOGV
      ESP_LOGV(TAG, "Writing out %u bytes via SPI bus in this order:", this->output_bytes_.size());
      for (auto byte = this->output_bytes_.rbegin(); byte != this->output_bytes_.rend(); ++byte)
        ESP_LOGV(TAG, "  0x%02X", *byte);
#endif
      this->enable();
      this->write_array(this->output_bytes_);
      this->disable();
      ESP_LOGV(TAG, "Pulsing the latch pin to set registers.");
      this->latch_pin_->digital_write(true);
      this->latch_pin_->digital_write(false);
    }

    void HV5222Pin::digital_write(bool value) { this->parent_->digital_write_(this->pin_, value != this->inverted_); }

    std::string HV5222Pin::dump_summary() const { return str_snprintf("%u GPIO output via HV5222", 27, this->pin_); }

  }  // namespace hv5222
}  // namespace esphome
