from ipywidgets import widgets
from corrcalculator import CorrCalculator
from dataloader import DataLoader
import plotly.graph_objects as go


class CorrelationApp:
    def __init__(self):
        self._register_figure()
        self._register_widgets()
        self._observe_events()
        self.calculator = None

    def run(self):
        return widgets.VBox([self._vbox1, self._vbox2, self._vbox3])

    def _register_widgets(self):

        self._und_options = ["NESN.SW", "NOVN.SW", "ROG.SW", "GIVN.SW", "TSLA", "VOW3.DE"]
        self._und1 = widgets.Dropdown(
            options=self._und_options,
            description="Underlying1:",
            value=None)
        self._und2 = widgets.Dropdown(
            options=self._und_options,
            description="Underlying2:",
            value=None)

        self._und1_previous_value = self._und1.value
        self._und2_previous_value = self._und2.value

        self._methods = widgets.Dropdown(
            options=["Quantile", "SMA", "EWMA"],
            description="Method:")
        self._quantiles = widgets.IntSlider(
            value=90,
            min=0,
            max=100,
            step=5,
            description="Quantile:",
            continuous_update=True)
        self._apply_max = widgets.Checkbox(
            description="ApplyMax",
            value=True)
        self._smoothing_windows = widgets.SelectionSlider(
            options=CorrelationApp._slide_options(),
            value=756,
            description="Smoothing:",
            continuous_update=True)
        self._corr_windows = widgets.SelectionSlider(
            options=CorrelationApp._slide_options(),
            value=252,
            description="Corr Window:",
            continuous_update=True)
        self._result = widgets.HTML(
            value="",
            placeholder="",
            description="")
        self._returns = widgets.Dropdown(
            options=[("1D", 1), ("5D", 5), ("2D", 2), ("3D", 3), ("4D", 4)],
            value=1,
            description="Return:")

        hbox1 = widgets.HBox([self._und1, self._und2])
        hbox2 = widgets.HBox([self._methods, self._quantiles, self._apply_max])
        hbox3 = widgets.HBox([self._returns, self._smoothing_windows, self._corr_windows])
        self._vbox1 = widgets.VBox([hbox1])
        self._vbox2 = widgets.VBox([hbox2, hbox3, self._figure])
        self._vbox2.layout.visibility = "hidden"
        self._vbox3 = widgets.VBox([self._result])

    def _register_figure(self):

        trace1 = go.Scatter(x=[],
                            y=[],
                            mode='lines',
                            name="",
                            line=dict(color='royalblue'))

        trace2 = go.Scatter(x=[],
                            y=[],
                            mode='lines',
                            name="",
                            line=dict(color='orangered'))

        self._figure = go.FigureWidget(data=[trace1, trace2])
        self._figure.update_layout(
            xaxis_title="Dates",
            yaxis_title="Values",
            legend=dict(orientation="h", y=1.02, yanchor="bottom"),
            height=450
        )

    def _event_handler(self, _):

        if self._und1.value is not None and self._und2.value is not None:
            if self._und1.value != self._und1_previous_value or self._und2.value != self._und2_previous_value:
                try:
                    data = DataLoader.load(self._und1.value, self._und2.value)
                    self.calculator = CorrCalculator(data)
                    self._vbox2.layout.visibility = "visible"
                    self._und1_previous_value = self._und1.value
                    self._und2_previous_value = self._und2.value
                except Exception as ex:
                    self._result.value = str(ex)
            if self.calculator is not None:
                self._event_handler_main_ui()

    def _event_handler_main_ui(self):
        if self._methods.value == "Quantile":
            m = "{0}Q".format(self._quantiles.value)
            self._quantiles.layout.visibility = "visible"
        else:
            m = self._methods.value
            self._quantiles.layout.visibility = "hidden"
        calc = self.calculator
        corr = calc.calc_corr(self._returns.value, self._corr_windows.value, self._smoothing_windows.value, m,
                              self._apply_max.value)
        with self._figure.batch_update():
            self._figure.data[0].x = corr.index
            self._figure.data[0].y = corr[calc.corr_label_]
            self._figure.data[0].name = calc.corr_label_
            self._figure.data[1].x = corr.index
            self._figure.data[1].y = corr[calc.corr_label_final_]
            self._figure.data[1].name = calc.corr_label_final_
        self._result.value = "{0} = {1}".format(calc.corr_label_final_, calc.result_)

    def _observe_events(self):
        self._methods.observe(self._event_handler, names="value")
        self._quantiles.observe(self._event_handler, names="value")
        self._smoothing_windows.observe(self._event_handler, names="value")
        self._apply_max.observe(self._event_handler, names="value")
        self._returns.observe(self._event_handler, names="value")
        self._corr_windows.observe(self._event_handler, names="value")
        self._und1.observe(self._event_handler, names="value")
        self._und2.observe(self._event_handler, names="value")

    @staticmethod
    def _slide_options():
        return [("{0}M".format(int(d / 21)), d) for d in range(21, 1009, 21)]
