--
--  Copyright (C) 2026, Vadim Godunko
--
--  SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
--

--  This is ESP32S3 SoC specific package

pragma Ada_2022;

package ESPIDF.SOC.Clk_Tree
  with Pure
is

   type soc_module_clk_t is
     (SOC_MOD_CLK_CPU,
      SOC_MOD_CLK_RTC_FAST,
      SOC_MOD_CLK_RTC_SLOW,
      SOC_MOD_CLK_APB,
      SOC_MOD_CLK_PLL_F80M,
      SOC_MOD_CLK_PLL_F160M,
      SOC_MOD_CLK_PLL_D2,
      SOC_MOD_CLK_XTAL32K,
      SOC_MOD_CLK_RC_FAST,
      SOC_MOD_CLK_RC_FAST_D256,
      SOC_MOD_CLK_XTAL,
      SOC_MOD_CLK_TEMP_SENSOR,
      SOC_MOD_CLK_INVALID);
   for soc_module_clk_t use
     (SOC_MOD_CLK_CPU          => 1,
      SOC_MOD_CLK_RTC_FAST     => 2,
      SOC_MOD_CLK_RTC_SLOW     => 3,
      SOC_MOD_CLK_APB          => 4,
      SOC_MOD_CLK_PLL_F80M     => 5,
      SOC_MOD_CLK_PLL_F160M    => 6,
      SOC_MOD_CLK_PLL_D2       => 7,
      SOC_MOD_CLK_XTAL32K      => 8,
      SOC_MOD_CLK_RC_FAST      => 9,
      SOC_MOD_CLK_RC_FAST_D256 => 10,
      SOC_MOD_CLK_XTAL         => 11,
      SOC_MOD_CLK_TEMP_SENSOR  => 12,
      SOC_MOD_CLK_INVALID      => 13);

   type soc_periph_rmt_clk_src_t is
     (RMT_CLK_SRC_APB,
      RMT_CLK_SRC_RC_FAST,
      RMT_CLK_SRC_XTAL);
   for soc_periph_rmt_clk_src_t use
     (RMT_CLK_SRC_APB     => SOC_MOD_CLK_APB'Enum_Rep,
      RMT_CLK_SRC_RC_FAST => SOC_MOD_CLK_RC_FAST'Enum_Rep,
      RMT_CLK_SRC_XTAL    => SOC_MOD_CLK_XTAL'Enum_Rep);
   function RMT_CLK_SRC_DEFAULT return soc_periph_rmt_clk_src_t
   is (soc_periph_rmt_clk_src_t'Enum_Val (SOC_MOD_CLK_APB'Enum_Rep))
   with Static;

end ESPIDF.SOC.Clk_Tree;
